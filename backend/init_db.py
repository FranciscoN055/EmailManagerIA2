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
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            print("🚀 Initializing database...")
            
            # Run all pending migrations
            upgrade()
            
            print("✅ Database initialized successfully!")
            print("📊 Tables created:")
            print("   - users")
            print("   - email_accounts") 
            print("   - emails")
            
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    init_database()
