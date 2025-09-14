import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    """Create and configure the Flask application."""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from .config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Configure CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Import models (this ensures they are registered with SQLAlchemy)
    from .models import User, EmailAccount, Email
    
    # Health check endpoints (before blueprints)
    @app.route('/api/health')
    def health_check():
        """Simple health check endpoint."""
        return {
            'status': 'healthy',
            'message': 'Email Manager IA API is running',
            'version': '1.0.0',
            'environment': app.config.get('FLASK_ENV', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }
    
    @app.route('/api/ping')
    def ping():
        """Keep alive endpoint to prevent sleep on free tier."""
        return {
            'status': 'pong',
            'message': 'Server is awake',
            'timestamp': datetime.now().isoformat()
        }
    
    @app.route('/api/debug')
    def debug():
        """Debug endpoint to test CORS and connectivity."""
        from flask import request
        return {
            'status': 'ok',
            'message': 'Backend is responding',
            'cors_origins': app.config.get('CORS_ORIGINS', []),
            'request_origin': request.headers.get('Origin', 'No origin'),
            'request_method': request.method,
            'timestamp': datetime.now().isoformat()
        }
    
    @app.route('/api/debug/env')
    def debug_env():
        """Debug endpoint to check environment variables."""
        return {
            'status': 'ok',
            'environment': app.config.get('FLASK_ENV', 'unknown'),
            'microsoft_config': {
                'client_id': app.config.get('MICROSOFT_CLIENT_ID', 'Not set'),
                'tenant_id': app.config.get('MICROSOFT_TENANT_ID', 'Not set'),
                'redirect_uri': app.config.get('MICROSOFT_REDIRECT_URI', 'Not set'),
                'authority': app.config.get('MICROSOFT_AUTHORITY', 'Not set'),
                'scopes': app.config.get('MICROSOFT_SCOPE', [])
            },
            'database_url': app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50] + '...' if app.config.get('SQLALCHEMY_DATABASE_URI') else 'Not set',
            'timestamp': datetime.now().isoformat()
        }
    
    # Register blueprints
    from .routes import auth_bp, emails_bp, microsoft_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(emails_bp, url_prefix='/api/emails')
    app.register_blueprint(microsoft_bp, url_prefix='/api/microsoft')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'error': 'Invalid token'}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'error': 'Authorization token is required'}, 401
    
    # Database health check endpoint
    @app.route('/api/health/db')
    def health_check_db():
        """Health check endpoint with database test."""
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return {
            'status': 'healthy',
            'message': 'Email Manager IA API is running',
            'version': '1.0.0',
            'database': db_status,
            'environment': app.config.get('FLASK_ENV', 'unknown'),
            'timestamp': datetime.now().isoformat()
        }
    
    # Database initialization endpoint
    @app.route('/api/init-db')
    def init_database_endpoint():
        """Initialize database tables endpoint."""
        try:
            print("🚀 Initializing database from endpoint...")
            
            # Create all tables
            db.create_all()
            print("✅ Tables created successfully!")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Tables created: {tables}")
            
            return {
                'status': 'success',
                'message': 'Database initialized successfully',
                'tables': tables,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error initializing database: {str(e)}")
            return {
                'status': 'error',
                'message': f'Database initialization failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, 500
    
    # Root endpoint
    @app.route('/')
    def root():
        """Root endpoint with API information."""
        return {
            'message': 'Welcome to Email Manager IA API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth',
                'emails': '/api/emails',
                'microsoft': '/api/microsoft'
            }
        }
    
    return app

def init_db(app):
    """Initialize database with sample data if needed."""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Add any initial data here if needed
        print("Database initialized successfully!")

# CLI command for database initialization
def register_commands(app):
    """Register CLI commands."""
    
    @app.cli.command()
    def init_db_command():
        """Initialize the database."""
        init_db(app)
        print('Initialized the database.')
    
    @app.cli.command()
    def reset_db_command():
        """Reset the database (WARNING: This will delete all data!)."""
        db.drop_all()
        db.create_all()
        print('Database has been reset.')