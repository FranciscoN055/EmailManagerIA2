#!/usr/bin/env python3
"""
PostgreSQL database initialization script for Email Manager IA
This script handles psycopg2 compatibility issues
"""

import os
import sys
from flask import Flask

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database_postgres():
    """Initialize PostgreSQL database with error handling."""
    try:
        print("🚀 Starting PostgreSQL database initialization...")
        
        # Try to import psycopg2
        try:
            import psycopg2
            print("✅ psycopg2 imported successfully")
        except ImportError as e:
            print(f"❌ psycopg2 import failed: {e}")
            print("🔄 Falling back to SQLite...")
            return False
        
        # Create Flask app
        from app import create_app, db
        app = create_app()
        print(f"✅ Flask app created with environment: {app.config.get('FLASK_ENV', 'unknown')}")
        
        with app.app_context():
            print("🚀 Initializing PostgreSQL database...")
            print(f"📊 Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")
            
            # Test database connection
            try:
                db.session.execute('SELECT 1')
                print("✅ Database connection successful!")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
            
            # Create all tables using migrations
            print("🔄 Running database migrations...")
            from flask_migrate import upgrade
            upgrade()
            print("✅ Migrations completed successfully!")
            
            # Also create tables directly as backup
            print("🔄 Creating database tables directly...")
            db.create_all()
            print("✅ Tables created successfully!")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tables created: {tables}")
            
            print("✅ PostgreSQL database initialized successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error initializing PostgreSQL database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = init_database_postgres()
    if not success:
        print("🔄 PostgreSQL initialization failed, falling back to SQLite...")
        sys.exit(1)
    else:
        print("✅ PostgreSQL initialization completed successfully!")
        sys.exit(0)
