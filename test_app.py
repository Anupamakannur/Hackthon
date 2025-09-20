#!/usr/bin/env python3
"""
Test script to identify and fix issues with the Resume Evaluator System
"""

import sys
import os
import traceback

def test_imports():
    """Test all imports to identify missing dependencies"""
    print("Testing imports...")
    
    try:
        # Test basic imports
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"✗ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import nltk
        print("✓ NLTK imported successfully")
    except ImportError as e:
        print(f"✗ NLTK import failed: {e}")
        return False
    
    try:
        import sklearn
        print("✓ scikit-learn imported successfully")
    except ImportError as e:
        print(f"✗ scikit-learn import failed: {e}")
        return False
    
    try:
        import PyPDF2
        print("✓ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"✗ PyPDF2 import failed: {e}")
        return False
    
    try:
        import docx
        print("✓ python-docx imported successfully")
    except ImportError as e:
        print(f"✗ python-docx import failed: {e}")
        return False
    
    try:
        import openai
        print("✓ OpenAI imported successfully")
    except ImportError as e:
        print(f"✗ OpenAI import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test app creation"""
    print("\nTesting app creation...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        # Test importing app
        from app import create_app
        print("✓ App module imported successfully")
        
        # Test creating app
        app = create_app()
        print("✓ App created successfully")
        
        # Test app context
        with app.app_context():
            print("✓ App context works")
        
        return True
        
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        traceback.print_exc()
        return False

def test_database():
    """Test database operations"""
    print("\nTesting database...")
    
    try:
        from app import create_app, db
        app = create_app()
        
        with app.app_context():
            # Test database creation
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Test basic query
            from models import User
            user_count = User.query.count()
            print(f"✓ Database query works (users: {user_count})")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("Resume Evaluator System - Diagnostic Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please install missing dependencies:")
        print("pip install -r requirements.txt")
        return False
    
    # Test app creation
    if not test_app_creation():
        print("\n❌ App creation failed. Check the error above.")
        return False
    
    # Test database
    if not test_database():
        print("\n❌ Database test failed. Check the error above.")
        return False
    
    print("\n✅ All tests passed! The app should work now.")
    print("\nTo run the app:")
    print("python app.py")
    
    return True

if __name__ == "__main__":
    main()
