from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

microsoft_bp = Blueprint('microsoft', __name__)

@microsoft_bp.route('/status')
def microsoft_status():
    """Check Microsoft Graph integration status."""
    return {
        'status': 'active',
        'message': 'Microsoft Graph integration system is running'
    }

# Additional Microsoft Graph routes will be implemented in the next phase