#!/usr/bin/env python
import os
import sys


def main():
    """Run Django management commands."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yml_validator.settings')
    
    # Handle different argument patterns
    if len(sys.argv) == 1:
        # No arguments - default runserver
        sys.argv.extend(['runserver', '--noreload'])
    elif len(sys.argv) == 2:
        if sys.argv[1] == 'runserver':
            # Just 'runserver' command
            sys.argv.append('--noreload')
        elif ':' in sys.argv[1] or sys.argv[1].isdigit():
            # Direct host:port or port argument
            host_port = sys.argv[1]
            sys.argv = [sys.argv[0], 'runserver', host_port, '--noreload']
    elif len(sys.argv) == 3 and sys.argv[1] == 'runserver':
        # runserver with host:port
        sys.argv.append('--noreload')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
