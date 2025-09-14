import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key-for-development-only'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'production'
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'fallback-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///email_manager.db'
    
    # Fallback to SQLite if PostgreSQL fails
    if SQLALCHEMY_DATABASE_URI.startswith('postgresql://'):
        try:
            import psycopg2
        except ImportError:
            print("Warning: psycopg2 not available, falling back to SQLite")
            SQLALCHEMY_DATABASE_URI = 'sqlite:///email_manager.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Microsoft Graph API Configuration
    MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID')
    MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET')
    MICROSOFT_TENANT_ID = os.environ.get('MICROSOFT_TENANT_ID') or 'common'
    MICROSOFT_AUTHORITY = f"https://login.microsoftonline.com/{os.environ.get('MICROSOFT_TENANT_ID') or 'common'}"
    MICROSOFT_SCOPE = [
        'https://graph.microsoft.com/User.Read',
        'https://graph.microsoft.com/Mail.ReadWrite',
        'https://graph.microsoft.com/Mail.Send',
        'offline_access'
    ]
    MICROSOFT_REDIRECT_URI = os.environ.get('MICROSOFT_REDIRECT_URI') or 'https://email-manager-ia-testing.vercel.app/auth/callback'
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = 'gpt-4'
    OPENAI_MAX_TOKENS = 1000
    OPENAI_TEMPERATURE = 0.3
    
    # Redis Configuration (for Celery)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Email Processing Configuration
    MAX_EMAILS_PER_SYNC = 100
    SYNC_INTERVAL_MINUTES = 15
    AI_CLASSIFICATION_BATCH_SIZE = 10
    
    # CORS Configuration
    CORS_ORIGINS = [
        'http://localhost:3000', 'http://localhost:5173', 'http://localhost:5174', 
        'http://localhost:5175', 'http://localhost:5176', 'http://localhost:5177', 
        'http://localhost:5178', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174',
        'http://127.0.0.1:5175', 'http://192.168.1.37:5173', 'http://192.168.1.37:5174',
        'https://email-manager-ia-testing.vercel.app',
        'https://email-manager-ia-testing-mj1cw77jx.vercel.app',
        'https://email-manager-ia-testiong-7wyk0l360.vercel.app'
    ]

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'
    
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Override with production-specific settings
    CORS_ORIGINS = [
        'https://emailmanageriatesting.onrender.com',
        'https://email-manager-ia-testing.vercel.app',
        'https://email-manager-ia-testing-mj1cw77jx.vercel.app',
        'https://email-manager-ia-testiong-7wyk0l360.vercel.app',
        'http://localhost:3000',
        'http://localhost:5173'
    ]
    MICROSOFT_REDIRECT_URI = os.environ.get('MICROSOFT_REDIRECT_URI') or 'https://emailmanageriatesting.onrender.com/auth/callback'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = 1  # 1 second for testing

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}