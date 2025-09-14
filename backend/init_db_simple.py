#!/usr/bin/env python3
"""
Simple database initialization script for Email Manager IA
This script creates the database tables using db.create_all() as fallback
"""

import os
import sys
from flask import Flask

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

def init_database_simple():
    """Initialize the database using db.create_all()."""
    try:
        print("🚀 Starting simple database initialization...")
        
        # Create Flask app
        app = create_app()
        print(f"✅ Flask app created with environment: {app.config.get('FLASK_ENV', 'unknown')}")
        
        with app.app_context():
            print("🚀 Creating database tables...")
            print(f"📊 Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")
            
            # Create all tables
            db.create_all()
            print("✅ Tables created successfully!")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tables created: {tables}")
            
            # Test database connection
            try:
                db.session.execute('SELECT 1')
                print("✅ Database connection test successful!")
            except Exception as e:
                print(f"⚠️ Database connection test failed: {e}")
            
            print("✅ Database initialized successfully!")
            
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    init_database_simple()
