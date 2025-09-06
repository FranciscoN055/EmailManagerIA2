#!/usr/bin/env python3
"""
Email Manager IA Backend Server
Main entry point for running the Flask application.
"""

import os
from app import create_app, register_commands

# Create Flask app
app = create_app()

# Register CLI commands
register_commands(app)

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Get debug mode from environment
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting Email Manager IA API server...")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Port: {port}")
    print(f"Debug mode: {debug}")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )