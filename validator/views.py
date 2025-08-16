from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import yaml
import json
import io
import re
from ruamel.yaml import YAML
from yaml.constructor import ConstructorError


class DuplicateKeyError(Exception):
    """Custom exception for duplicate keys in YAML."""
    pass


class SafeLoaderWithDuplicateKeyCheck(yaml.SafeLoader):
    """Custom YAML loader that detects duplicate keys."""
    
    def construct_mapping(self, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                # Found duplicate key - raise error with line information
                raise DuplicateKeyError(
                    f"Duplicate key '{key}' found at line {key_node.start_mark.line + 1}"
                )
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


def validate_yaml_with_duplicate_check(yaml_content):
    """
    Validate YAML content with proper duplicate key detection.
    Returns (is_valid, parsed_data, error_message, line_number)
    """
    try:
        # Use custom loader to detect duplicate keys
        parsed_data = yaml.load(yaml_content, Loader=SafeLoaderWithDuplicateKeyCheck)
        return True, parsed_data, None, None
    except DuplicateKeyError as e:
        # Extract line number from duplicate key error
        error_msg = str(e)
        line_number = None
        if "line" in error_msg:
            try:
                line_number = int(error_msg.split("line ")[1].split()[0])
            except (IndexError, ValueError):
                pass
        return False, None, error_msg, line_number
    except yaml.YAMLError as e:
        # Handle other YAML errors
        line_number = None
        if hasattr(e, 'problem_mark') and e.problem_mark:
            line_number = e.problem_mark.line + 1
        return False, None, str(e), line_number
    except Exception as e:
        return False, None, f"Unexpected error: {str(e)}", None


def fix_yaml_indentation(yaml_content):
    """
    Fix YAML indentation issues using a simpler, more reliable approach.
    """
    lines = yaml_content.split('\n')
    corrected_lines = []
    current_section = None
    section_indent = 0
    
    for i, line in enumerate(lines):
        if not line.strip():  # Empty line
            corrected_lines.append(line)
            continue
            
        if line.strip().startswith('#'):  # Comment line
            corrected_lines.append(line)
            continue
        
        stripped = line.strip()
        
        # Check if this is a top-level key (no indentation and ends with colon)
        if ':' in stripped and not line.startswith(' ') and not line.startswith('\t'):
            if stripped.endswith(':') or (': ' in stripped and stripped.split(': ', 1)[1].strip()):
                # This is a top-level section
                current_section = stripped.split(':')[0]
                section_indent = 0
                corrected_lines.append(stripped)
                continue
        
        # If we're inside a section, ensure proper indentation
        if current_section and ':' in stripped:
            # This should be indented under the current section
            key = stripped.split(':')[0].strip()
            value = stripped.split(':', 1)[1].strip() if ':' in stripped else ''
            
            if value:
                corrected_line = '  ' + key + ': ' + value
            else:
                corrected_line = '  ' + key + ':'
                
            corrected_lines.append(corrected_line)
            continue
        
        # Handle list items
        if stripped.startswith('-'):
            if current_section:
                corrected_lines.append('  ' + stripped)
            else:
                corrected_lines.append(stripped)
            continue
        
        # For other lines, try to maintain reasonable indentation
        if current_section:
            corrected_lines.append('  ' + stripped)
        else:
            corrected_lines.append(stripped)
    
    return '\n'.join(corrected_lines)


def index(request):
    """Main view for the YAML validator interface."""
    return render(request, 'validator/index.html')


@csrf_exempt
def validate_yaml(request):
    """AJAX endpoint to validate YAML content."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yaml_content = data.get('yaml_content', '')
            
            if not yaml_content.strip():
                return JsonResponse({
                    'valid': False,
                    'error': 'Please enter some YAML content to validate.',
                    'line_number': None
                })
            
            # Use enhanced validation with duplicate key detection
            is_valid, parsed_data, error_message, line_number = validate_yaml_with_duplicate_check(yaml_content)
            
            if is_valid:
                return JsonResponse({
                    'valid': True,
                    'message': 'Valid YAML content!',
                    'parsed_data': parsed_data
                })
            else:
                return JsonResponse({
                    'valid': False,
                    'error': error_message,
                    'line_number': line_number
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'valid': False,
                'error': 'Invalid request format.',
                'line_number': None
            })
    
    return JsonResponse({
        'valid': False,
        'error': 'Only POST requests are allowed.',
        'line_number': None
    })


@csrf_exempt
def correct_yaml(request):
    """AJAX endpoint to auto-correct YAML content."""
    if request.method == 'POST':
        try:
            # Add debugging
            print(f"Received correction request: {request.body[:100]}...")
            
            data = json.loads(request.body)
            yaml_content = data.get('yaml_content', '')
            
            if not yaml_content.strip():
                return JsonResponse({
                    'success': False,
                    'error': 'Please enter some YAML content to correct.',
                    'corrected_yaml': ''
                })
            
            try:
                # First, try enhanced validation with duplicate key detection
                is_valid, parsed_data, error_message, line_number = validate_yaml_with_duplicate_check(yaml_content)
                
                if not is_valid:
                    # If validation fails due to duplicate keys, return specific error
                    if "Duplicate key" in error_message:
                        return JsonResponse({
                            'success': False,
                            'error': f'Cannot correct YAML: {error_message}',
                            'corrected_yaml': '',
                            'line_number': line_number
                        })
                    # For other errors, continue with correction attempts below
                    raise yaml.YAMLError(error_message)
                
                print(f"Parsed data successfully: {type(parsed_data)}")
                
                if parsed_data is None:
                    print("Parsed data is None")
                    return JsonResponse({
                        'success': False,
                        'error': 'YAML content is empty or invalid.',
                        'corrected_yaml': ''
                    })
                
                # Use ruamel.yaml to format the YAML properly
                yaml_formatter = YAML()
                yaml_formatter.preserve_quotes = True
                yaml_formatter.width = 4096
                yaml_formatter.indent(mapping=2, sequence=4, offset=2)
                
                # Create a string buffer to capture the output
                output = io.StringIO()
                yaml_formatter.dump(parsed_data, output)
                corrected_yaml = output.getvalue()
                
                response_data = {
                    'success': True,
                    'message': 'YAML has been auto-corrected and formatted!',
                    'corrected_yaml': corrected_yaml,
                    'original_valid': True
                }
                print(f"Returning success response: {response_data['success']}")
                return JsonResponse(response_data)
                
            except yaml.YAMLError as e:
                # Enhanced YAML correction for complex indentation issues
                print(f"YAML parsing failed, attempting intelligent correction: {str(e)}")
                
                # Try intelligent indentation correction
                corrected_content = fix_yaml_indentation(yaml_content)
                
                # Try to parse the corrected content
                try:
                    corrected_parsed = yaml.safe_load(corrected_content)
                    if corrected_parsed is not None:
                        # Use ruamel.yaml to format the corrected YAML properly
                        yaml_formatter = YAML()
                        yaml_formatter.preserve_quotes = True
                        yaml_formatter.width = 4096
                        yaml_formatter.indent(mapping=2, sequence=4, offset=2)
                        
                        output = io.StringIO()
                        yaml_formatter.dump(corrected_parsed, output)
                        final_corrected_yaml = output.getvalue()
                        
                        return JsonResponse({
                            'success': True,
                            'message': 'YAML indentation issues have been automatically corrected!',
                            'corrected_yaml': final_corrected_yaml,
                            'original_valid': False
                        })
                except yaml.YAMLError:
                    pass
                
                # If intelligent correction fails, try basic corrections
                corrected_content = yaml_content
                original_error = str(e)
                
                # Basic corrections for common YAML issues
                lines = corrected_content.split('\n')
                corrected_lines = []
                changes_made = False
                
                for line in lines:
                    original_line = line
                    
                    # Fix missing spaces after colons
                    if ':' in line and not line.strip().startswith('#'):
                        # Find the colon and ensure there's a space after it
                        colon_index = line.find(':')
                        if colon_index != -1 and colon_index < len(line) - 1:
                            if line[colon_index + 1] != ' ' and line[colon_index + 1] != '\n':
                                line = line[:colon_index + 1] + ' ' + line[colon_index + 1:]
                                changes_made = True
                    
                    # Fix inconsistent indentation (convert tabs to spaces)
                    if '\t' in line:
                        line = line.replace('\t', '  ')
                        changes_made = True
                    
                    corrected_lines.append(line)
                
                corrected_content = '\n'.join(corrected_lines)
                
                # Try to parse the corrected content
                try:
                    yaml.safe_load(corrected_content)
                    return JsonResponse({
                        'success': True,
                        'message': 'YAML has been auto-corrected! Basic formatting issues were fixed.',
                        'corrected_yaml': corrected_content,
                        'original_valid': False
                    })
                except yaml.YAMLError as correction_error:
                    # If still invalid, return the error with partial correction
                    line_number = None
                    if hasattr(correction_error, 'problem_mark') and correction_error.problem_mark:
                        line_number = correction_error.problem_mark.line + 1
                    
                    # Only show partial correction if we actually made changes
                    if changes_made:
                        return JsonResponse({
                            'success': False,
                            'error': f'YAML is still invalid after basic corrections: {str(correction_error)}',
                            'corrected_yaml': corrected_content,
                            'line_number': line_number,
                            'partial_correction': True
                        })
                    else:
                        # No changes were made, return original error
                        original_line_number = None
                        if hasattr(e, 'problem_mark') and e.problem_mark:
                            original_line_number = e.problem_mark.line + 1
                        
                        return JsonResponse({
                            'success': False,
                            'error': f'Unable to auto-correct YAML: {original_error}',
                            'corrected_yaml': '',
                            'line_number': original_line_number,
                            'partial_correction': False
                        })
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid request format.',
                'corrected_yaml': ''
            })
        except Exception as e:
            print(f"Unexpected error in correct_yaml: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Server error: {str(e)}',
                'corrected_yaml': ''
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Only POST requests are allowed.',
        'corrected_yaml': ''
    })
