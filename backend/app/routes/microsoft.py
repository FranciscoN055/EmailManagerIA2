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

@microsoft_bp.route('/auth/callback', methods=['GET', 'POST'])
def microsoft_callback():
    """Handle Microsoft OAuth2 callback."""
    try:
        # Handle both GET (direct from Microsoft) and POST (from frontend)
        if request.method == 'POST':
            data = request.get_json()
            code = data.get('code') if data else None
            state = None  # Frontend doesn't send state
            error = None
        else:
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
        
        # Validate state parameter (only for GET requests)
        if request.method == 'GET':
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
        
        # Debug: Log token info
        logger.info(f"Token received - type: {type(access_token)}, length: {len(access_token) if access_token else 0}")
        logger.info(f"Token scopes from result: {token_result.get('scope', 'No scope info')}")
        logger.info(f"Full token result keys: {list(token_result.keys()) if token_result else 'No result'}")
        
        # Log what scopes we actually got vs what we requested
        if 'scope' in token_result:
            granted_scopes = token_result['scope'].split(' ')
            requested_scopes = service.scopes
            logger.info(f"Requested scopes: {requested_scopes}")
            logger.info(f"Granted scopes: {granted_scopes}")
            
            # Check if we got the mail permissions
            has_mail_read = any('Mail.Read' in scope for scope in granted_scopes)
            has_mail_write = any('Mail.ReadWrite' in scope for scope in granted_scopes)
            logger.info(f"Has Mail.Read permission: {has_mail_read}")
            logger.info(f"Has Mail.ReadWrite permission: {has_mail_write}")
        
        # Test the token immediately
        test_result = service.test_token(access_token)
        logger.info(f"Token test result: {test_result}")
        
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
                display_name=profile.get('displayName', ''),
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
    """
    Devuelve el nombre, correo, si tiene foto y otros datos del perfil de Microsoft.
    """
    try:
        user_id = get_jwt_identity()
        email_account = EmailAccount.query.filter_by(
            user_id=user_id,
            provider='microsoft',
            is_active=True
        ).first()
        if not email_account:
            return jsonify({'success': False, 'error': 'Microsoft account not connected'}), 400

        service = MicrosoftGraphService()
        profile = service.get_user_profile(email_account.access_token)
        has_photo = False
        if profile:
            photo_data = service.get_user_photo(email_account.access_token)
            has_photo = photo_data is not None
            return jsonify({
                'success': True,
                'name': profile.get('displayName'),
                'email': profile.get('mail') or profile.get('userPrincipalName'),
                'has_photo': has_photo,
                'job_title': profile.get('jobTitle', ''),
                'department': profile.get('department', ''),
                'office_location': profile.get('officeLocation', '')
            })
        else:
            return jsonify({'success': False, 'error': 'Profile not found'}), 404
    except Exception as e:
        logger.error(f"Error getting Microsoft profile: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get profile'}), 500

@microsoft_bp.route('/profile/photo')
@jwt_required()
def get_microsoft_profile_photo():
    """Get Microsoft user profile photo."""
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
        photo_data = service.get_user_photo(email_account.access_token)
        
        if photo_data:
            from flask import send_file
            import io
            return send_file(
                io.BytesIO(photo_data),
                mimetype='image/jpeg',
                as_attachment=False
            )
        else:
            return jsonify({
                'success': False,
                'error': 'No profile photo available'
            }), 404
    
    except Exception as e:
        logger.error(f"Error getting Microsoft profile photo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get profile photo'
        }), 500

@microsoft_bp.route('/test-permissions')
@jwt_required()
def test_permissions():
    """Test what permissions the current token actually has."""
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
        
        # Test 1: Basic profile access
        profile_test = service.test_token(email_account.access_token)
        
        # Test 2: Try to get mail folders (should work with Mail.Read)
        folders_test = None
        try:
            folders_response = service.get_mail_folders(email_account.access_token)
            folders_test = {
                'success': True,
                'folders_count': len(folders_response.get('value', [])) if folders_response else 0
            }
        except Exception as e:
            folders_test = {'success': False, 'error': str(e)}
        
        # Test 3: Try to get one email (most restrictive test)
        emails_test = None
        try:
            emails_response = service.get_user_emails(email_account.access_token, top=1)
            emails_test = {
                'success': True,
                'emails_count': len(emails_response.get('value', [])) if emails_response else 0
            }
        except Exception as e:
            emails_test = {'success': False, 'error': str(e)}
        
        return jsonify({
            'success': True,
            'token_exists': bool(email_account.access_token),
            'token_length': len(email_account.access_token) if email_account.access_token else 0,
            'tests': {
                'profile_access': profile_test,
                'mail_folders': folders_test,
                'emails_access': emails_test
            }
        })
    
    except Exception as e:
        logger.error(f"Error testing permissions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to test permissions'
        }), 500

@microsoft_bp.route('/debug-token')
@jwt_required()
def debug_token():
    """Debug endpoint to test token validity."""
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
        
        # Test the token with a simple API call
        test_result = service.test_token(email_account.access_token)
        
        # Also test direct email access
        import requests
        headers = {'Authorization': f'Bearer {email_account.access_token}'}
        
        # Test 1: User profile (should work)
        profile_response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers, timeout=10)
        
        # Test 2: Mail folders (requires Mail.Read)
        folders_response = requests.get('https://graph.microsoft.com/v1.0/me/mailFolders', headers=headers, timeout=10)
        
        # Test 3: Emails (most restrictive)
        emails_response = requests.get('https://graph.microsoft.com/v1.0/me/messages?$top=1', headers=headers, timeout=10)
        
        # Test 4: Send mail permissions (try to get send mail endpoint info)
        send_mail_response = requests.get('https://graph.microsoft.com/v1.0/me/sendMail', headers=headers, timeout=10)
        
        return jsonify({
            'success': True,
            'token_exists': bool(email_account.access_token),
            'token_preview': email_account.access_token[:10] + '...' if email_account.access_token else None,
            'tests': {
                'profile': {'status': profile_response.status_code, 'ok': profile_response.status_code == 200},
                'folders': {'status': folders_response.status_code, 'ok': folders_response.status_code == 200, 'text': folders_response.text[:200] if folders_response.status_code != 200 else 'OK'},
                'emails': {'status': emails_response.status_code, 'ok': emails_response.status_code == 200, 'text': emails_response.text[:200] if emails_response.status_code != 200 else 'OK'},
                'send_mail': {'status': send_mail_response.status_code, 'ok': send_mail_response.status_code in [200, 405], 'text': send_mail_response.text[:200] if send_mail_response.status_code not in [200, 405] else 'OK'}
            }
        })
    
    except Exception as e:
        logger.error(f"Error debugging token: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to debug token'
        }), 500

@microsoft_bp.route('/test-send-email')
@jwt_required()
def test_send_email():
    """Test sending a simple email to verify permissions."""
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
        
        # Test sending a simple email to yourself
        test_email = email_account.email_address
        test_subject = "Test Email from Email Manager IA"
        test_body = "<p>This is a test email to verify send permissions.</p>"
        
        success = service.send_email(
            access_token=email_account.access_token,
            to_email=test_email,
            subject=test_subject,
            body=test_body
        )
        
        return jsonify({
            'success': success,
            'message': 'Test email sent successfully' if success else 'Failed to send test email',
            'test_email': test_email
        })
    
    except Exception as e:
        logger.error(f"Error testing send email: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to test send email'
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