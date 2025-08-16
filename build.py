#!/usr/bin/env python3
import os
import subprocess
import sys

def build_executable():
    """Build the Django YAML validator executable using PyInstaller."""
    
    print("🔨 Building Django YAML Validator executable...")
    
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Build using spec file
    try:
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller', 
            'yml-validator.spec'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Build successful!")
        print(f"📁 Executable location: dist/yml-validator")
        print(f"🚀 Run with: ./dist/yml-validator")
        
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print(f"Error: {e.stderr}")
        return False
    
    return True

if __name__ == '__main__':
    build_executable()
