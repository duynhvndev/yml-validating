#!/usr/bin/env python3
"""
Setup script for Django YAML Validator
Creates database and prepares the project for building/running
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_project():
    """Initialize the Django project and create database."""
    
    print("🔧 Setting up Django YAML Validator...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yml_validator.settings')
    
    # Initialize Django
    django.setup()
    
    # Create database if it doesn't exist
    if not os.path.exists('db.sqlite3'):
        print("📊 Creating database...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Database created successfully!")
    else:
        print("📊 Database already exists, running migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed!")
    
    print("🎉 Setup completed! You can now:")
    print("   • Run directly: python manage.py runserver")
    print("   • Build executable: pyinstaller yml-validator.spec")

if __name__ == '__main__':
    setup_project()
