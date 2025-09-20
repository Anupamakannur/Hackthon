#!/usr/bin/env python3
"""
Quick Setup and Run Script for Resume Evaluator System
"""

import os
import sys
import subprocess

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    dependencies = [
        'flask',
        'werkzeug',
        'requests'
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep} already installed")
        except ImportError:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✓ {dep} installed")

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = [
        'templates',
        'static/css',
        'static/js',
        'uploads',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ {directory} created")

def main():
    """Main function"""
    print("=" * 60)
    print("Resume Evaluator System - Quick Setup")
    print("=" * 60)
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    print("To run the system:")
    print("1. python simple_app.py")
    print("2. Open http://localhost:5000 in your browser")
    print("=" * 60)
    
    # Ask if user wants to run now
    response = input("\nDo you want to run the system now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        print("\n🚀 Starting Resume Evaluator System...")
        print("Access at: http://localhost:5000")
        print("Press Ctrl+C to stop")
        print("-" * 60)
        
        # Import and run the simple app
        from simple_app import main as run_app
        run_app()
    else:
        print("Setup complete! Run 'python simple_app.py' when ready.")

if __name__ == "__main__":
    main()
