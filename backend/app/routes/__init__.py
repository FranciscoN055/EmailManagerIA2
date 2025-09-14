from .auth import auth_bp
from .emails import emails_bp
from .microsoft import microsoft_bp

# Health check endpoint
def create_health_route(app):
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'service': 'Email Manager IA'}

__all__ = ['auth_bp', 'emails_bp', 'microsoft_bp', 'create_health_route']