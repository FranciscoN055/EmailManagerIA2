from flask import Blueprint, request, jsonify, redirect, url_for, session
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.services.microsoft_graph import MicrosoftGraphService
from app.models.user import User
from app.models.email_account import EmailAccount
from app import db
import uuid
import logging

logger = logging.getLogger(__name__)
microsoft_bp = Blueprint('microsoft', __name__)

@microsoft_bp.route('/status')
def microsoft_status():
    """Check Microsoft Graph integration status."""
    service = MicrosoftGraphService()
    return jsonify(service.get_status())

@microsoft_bp.route('/auth/login')
def microsoft_login():
    """Initiate Microsoft OAuth2 login flow."""
    try:
        service = MicrosoftGraphService()
        state = str(uuid.uuid4())
        session['auth_state'] = state
        
        auth_url = service.get_auth_url(state=state)
        
        if not auth_url:
            return jsonify({
                'success': False,
                'error': 'Failed to generate authorization URL'
            }), 500
        
        return jsonify({
            'success': True,
            'auth_url': auth_url,
            'state': state
        })
    
    except Exception as e:
        logger.error(f"Error initiating Microsoft login: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Authentication initialization failed'
        }), 500

@microsoft_bp.route('/auth/callback')
def microsoft_callback():
    """Handle Microsoft OAuth2 callback."""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            logger.error(f"Microsoft OAuth error: {error}")
            return jsonify({
                'success': False,
                'error': f'OAuth error: {error}'
            }), 400
        
        if not code:
            return jsonify({
                'success': False,
                'error': 'Authorization code not provided'
            }), 400
        
        # Validate state parameter
        session_state = session.get('auth_state')
        if not session_state or state != session_state:
            return jsonify({
                'success': False,
                'error': 'Invalid state parameter'
            }), 400
        
        service = MicrosoftGraphService()
        
        # Exchange code for tokens
        token_result = service.exchange_code_for_tokens(code)
        
        if not token_result or 'access_token' not in token_result:
            return jsonify({
                'success': False,
                'error': 'Failed to obtain access token'
            }), 400
        
        access_token = token_result['access_token']
        refresh_token = token_result.get('refresh_token')
        
        # Get user profile
        profile = service.get_user_profile(access_token)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Failed to get user profile'
            }), 400
        
        # Find or create user
        user = User.query.filter_by(email=profile['mail'] or profile['userPrincipalName']).first()
        
        if not user:
            user = User(
                email=profile['mail'] or profile['userPrincipalName'],
                full_name=profile.get('displayName', ''),
                microsoft_user_id=profile['id'],
                is_active=True
            )
            db.session.add(user)
            db.session.flush()  # Get user ID
        else:
            user.microsoft_user_id = profile['id']
            user.full_name = profile.get('displayName', user.full_name)
            user.is_active = True
        
        # Create or update email account
        email_account = EmailAccount.query.filter_by(user_id=user.id, provider='microsoft').first()
        
        if not email_account:
            email_account = EmailAccount(
                user_id=user.id,
                email_address=profile['mail'] or profile['userPrincipalName'],
                provider='microsoft',
                is_primary=True,
                is_active=True
            )
            db.session.add(email_account)
        
        # Update tokens (encrypt in production)
        email_account.access_token = access_token
        email_account.refresh_token = refresh_token
        email_account.token_expires_at = None  # Will be handled by MSAL
        
        db.session.commit()
        
        # Generate JWT token for our application
        jwt_token = create_access_token(identity=user.id)
        
        # Clear session state
        session.pop('auth_state', None)
        
        return jsonify({
            'success': True,
            'message': 'Microsoft account connected successfully',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'name': user.full_name
            },
            'token': jwt_token
        })
    
    except Exception as e:
        logger.error(f"Error in Microsoft callback: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Authentication failed'
        }), 500

@microsoft_bp.route('/auth/disconnect', methods=['POST'])
@jwt_required()
def disconnect_microsoft():
    """Disconnect Microsoft account."""
    try:
        user_id = get_jwt_identity()
        
        # Find and deactivate email account
        email_account = EmailAccount.query.filter_by(
            user_id=user_id, 
            provider='microsoft'
        ).first()
        
        if email_account:
            email_account.is_active = False
            email_account.access_token = None
            email_account.refresh_token = None
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Microsoft account disconnected successfully'
        })
    
    except Exception as e:
        logger.error(f"Error disconnecting Microsoft account: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to disconnect account'
        }), 500

@microsoft_bp.route('/profile')
@jwt_required()
def get_microsoft_profile():
    """Get Microsoft user profile."""
    try:
        user_id = get_jwt_identity()
        
        email_account = EmailAccount.query.filter_by(
            user_id=user_id,
            provider='microsoft',
            is_active=True
        ).first()
        
        if not email_account:
            return jsonify({
                'success': False,
                'error': 'Microsoft account not connected'
            }), 400
        
        service = MicrosoftGraphService()
        profile = service.get_user_profile(email_account.access_token)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Failed to get profile data'
            }), 400
        
        return jsonify({
            'success': True,
            'profile': {
                'id': profile['id'],
                'email': profile['mail'] or profile['userPrincipalName'],
                'name': profile.get('displayName', ''),
                'job_title': profile.get('jobTitle', ''),
                'department': profile.get('department', ''),
                'office_location': profile.get('officeLocation', '')
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting Microsoft profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get profile'
        }), 500

@microsoft_bp.route('/folders')
@jwt_required()
def get_mail_folders():
    """Get user's mail folders."""
    try:
        user_id = get_jwt_identity()
        
        email_account = EmailAccount.query.filter_by(
            user_id=user_id,
            provider='microsoft',
            is_active=True
        ).first()
        
        if not email_account:
            return jsonify({
                'success': False,
                'error': 'Microsoft account not connected'
            }), 400
        
        service = MicrosoftGraphService()
        folders = service.get_mail_folders(email_account.access_token)
        
        if not folders:
            return jsonify({
                'success': False,
                'error': 'Failed to get mail folders'
            }), 400
        
        return jsonify({
            'success': True,
            'folders': folders.get('value', [])
        })
    
    except Exception as e:
        logger.error(f"Error getting mail folders: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get folders'
        }), 500