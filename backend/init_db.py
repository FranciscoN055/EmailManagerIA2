#!/usr/bin/env python3
"""
Database initialization script for Email Manager IA
This script creates the database tables using Flask-Migrate
"""

import os
import sys
from flask import Flask
from flask_migrate import upgrade

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def init_database():
    """Initialize the database with all migrations."""
    try:
        print("🚀 Starting database initialization...")
        
        # Create Flask app
        app = create_app()
        print(f"✅ Flask app created with environment: {app.config.get('FLASK_ENV', 'unknown')}")
        
        with app.app_context():
            print("🚀 Initializing database...")
            print(f"📊 Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")
            
            # Check database type
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
                print(f"📁 SQLite database file path: {db_path}")
                if os.path.exists(db_path):
                    print("✅ Database file exists")
                else:
                    print("⚠️ Database file does not exist, will be created")
            elif db_uri.startswith('postgresql://'):
                print("🐘 PostgreSQL database detected")
                print(f"📊 Database URI: {db_uri[:50]}...")
            else:
                print(f"📊 Database URI: {db_uri[:50]}...")
            
            # Run all pending migrations
            print("🔄 Running migrations...")
            upgrade()
            print("✅ Migrations completed successfully!")
            
            # Verify tables were created
            from app import db
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tables created: {tables}")
            
            print("✅ Database initialized successfully!")
            
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    init_database()
