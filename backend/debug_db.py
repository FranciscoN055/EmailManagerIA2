#!/usr/bin/env python3
"""
Database debugging script for Email Manager IA
This script helps diagnose database connection issues
"""

import os
import sys
from flask import Flask

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def debug_database():
    """Debug database configuration and connection."""
    try:
        print("🔍 Starting database debug...")
        
        # Create Flask app
        app = create_app()
        print(f"✅ Flask app created with environment: {app.config.get('FLASK_ENV', 'unknown')}")
        
        with app.app_context():
            # Check environment variables
            print("\n📊 Environment Variables:")
            print(f"  DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')}")
            print(f"  FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not set')}")
            
            # Check Flask config
            print("\n🔧 Flask Configuration:")
            print(f"  SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
            print(f"  FLASK_ENV: {app.config.get('FLASK_ENV', 'Not set')}")
            
            # Test database connection
            print("\n🔌 Testing Database Connection:")
            try:
                db.session.execute('SELECT 1')
                print("✅ Database connection successful!")
                
                # Check if tables exist
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"📊 Existing tables: {tables}")
                
                if 'users' in tables:
                    print("✅ 'users' table exists")
                else:
                    print("❌ 'users' table does not exist")
                    
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                
        print("\n✅ Debug completed!")
        
    except Exception as e:
        print(f"❌ Error during debug: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    debug_database()
