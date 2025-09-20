from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.microsoft_graph import MicrosoftGraphService
from app.services.openai_service import OpenAIService
from app.services.email_processor import EmailProcessor
from app.models.user import User
from app.models.email import Email
from app.models.email_account import EmailAccount
from app.utils.helpers import extract_email_preview, get_priority_from_urgency
from app import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
emails_bp = Blueprint('emails', __name__)

@emails_bp.route('/status')
def emails_status():
    """Check email system status."""
    return jsonify({
        'status': 'active',
        'message': 'Email management system is running'
    })

@emails_bp.route('/sync', methods=['POST'])
@jwt_required()
def sync_emails():
    """Sync emails from Microsoft Graph."""
    try:
        user_id = get_jwt_identity()
        logger.info(f"Starting email sync for user {user_id}")
        
        # Get email account
        email_account = EmailAccount.query.filter_by(
            user_id=user_id,
            provider='microsoft',
            is_active=True
        ).first()
        
        logger.info(f"Found email account: {email_account is not None}")
        
        if not email_account:
            logger.warning(f"No Microsoft account found for user {user_id}")
            return jsonify({
                'success': False,
                'error': 'Microsoft account not connected'
            }), 400
        
        # Get sync parameters
        data = request.get_json() or {}
        top = min(data.get('count', 50), 200)  # Max 200 emails per sync
        folder = data.get('folder', 'inbox')
        classify_immediately = data.get('classify', True)  # Auto-classify by default
        
        service = MicrosoftGraphService()
        
        # Check if we have a valid access token
        if not email_account.access_token:
            return jsonify({
                'success': False,
                'error': 'No access token available. Please reconnect your Microsoft account.'
            }), 401
        
        logger.info(f"Attempting to sync {top} emails from {folder} folder for user {user_id}")
        
        # Fetch emails from Microsoft Graph
        emails_data = service.get_user_emails(
            email_account.access_token,
            top=top,
            folder=folder
        )
        
        if not emails_data:
            logger.error(f"Failed to fetch emails - likely token expired for user {user_id}")
            return jsonify({
                'success': False,
                'error': 'Failed to fetch emails from Microsoft. Token may have expired. Please reconnect your account.'
            }), 401
            
        if 'value' not in emails_data:
            logger.error(f"Unexpected response format from Microsoft Graph: {emails_data}")
            return jsonify({
                'success': False,
                'error': 'Unexpected response format from Microsoft Graph'
            }), 400
        
        synced_count = 0
        skipped_count = 0
        classified_count = 0
        new_emails = []
        
        for email_data in emails_data['value']:
            try:
                # Check if email already exists
                existing_email = Email.query.filter_by(
                    microsoft_email_id=email_data['id']
                ).first()
                
                if existing_email:
                    # Update existing email's read status and other properties
                    updated = False
                    
                    # Check if isRead status changed
                    current_is_read = email_data.get('isRead', False)
                    if existing_email.is_read != current_is_read:
                        existing_email.is_read = current_is_read
                        updated = True
                        logger.info(f"Updated isRead status for email {existing_email.id}: {current_is_read}")
                    
                    # Check if importance changed
                    current_importance = email_data.get('importance', 'normal') == 'high'
                    if existing_email.is_important != current_importance:
                        existing_email.is_important = current_importance
                        updated = True
                    
                    # Check if flag status changed (starred)
                    flag_status = email_data.get('flag', {})
                    current_starred = flag_status.get('flagStatus', 'notFlagged') != 'notFlagged'
                    if existing_email.is_starred != current_starred:
                        existing_email.is_starred = current_starred
                        updated = True
                    
                    if updated:
                        existing_email.updated_at = datetime.now()
                        db.session.add(existing_email)
                        logger.info(f"Updated existing email {existing_email.id}")
                    
                    skipped_count += 1
                    continue
                
                # Extract email preview
                body_preview = extract_email_preview(
                    email_data.get('body', {}).get('content', ''),
                    max_length=500
                )
                
                # Create new email record
                email = Email(
                    email_account_id=email_account.id,
                    microsoft_email_id=email_data['id'],
                    subject=email_data.get('subject', ''),
                    sender_email=email_data.get('from', {}).get('emailAddress', {}).get('address', ''),
                    sender_name=email_data.get('from', {}).get('emailAddress', {}).get('name', ''),
                    recipient_emails=email_account.email_address,
                    body_content=email_data.get('body', {}).get('content', ''),
                    body_preview=body_preview,
                    received_at=datetime.fromisoformat(
                        email_data['receivedDateTime'].replace('Z', '+00:00')
                    ),
                    is_read=email_data.get('isRead', False),
                    has_attachments=email_data.get('hasAttachments', False),
                    urgency_category='medium',  # Default, will be updated by AI
                    priority_level=3,
                    ai_confidence=0.0,
                    processing_status='pending'
                )
                
                db.session.add(email)
                db.session.flush()  # Get email ID
                
                new_emails.append({
                    'email_id': str(email.id),
                    'subject': email.subject,
                    'sender_name': email.sender_name,
                    'sender_email': email.sender_email,
                    'body_preview': body_preview,
                    'received_at': email.received_at.isoformat()
                })
                
                synced_count += 1
                
            except Exception as e:
                logger.warning(f"Skipping email {email_data['id']} due to error: {str(e)}")
                skipped_count += 1
                continue
        
        # Commit emails first
        db.session.commit()
        
        # Classify emails with OpenAI if requested and we have new emails
        classification_results = {}
        if classify_immediately and new_emails:
            try:
                openai_service = OpenAIService()
                logger.info(f"Starting AI classification of {len(new_emails)} new emails")
                
                # Classify in batches
                classifications = openai_service.classify_batch(new_emails, batch_size=3)
                
                # Update emails with classification results
                for i, email_data in enumerate(new_emails):
                    if i < len(classifications):
                        classification = classifications[i]
                        
                        # Find and update the email
                        email = Email.query.get(email_data['email_id'])
                        if email:
                            email.urgency_category = classification.get('urgency_category', 'medium')
                            email.priority_level = get_priority_from_urgency(email.urgency_category)
                            email.ai_confidence = classification.get('confidence_score', 0.0)
                            email.ai_reasoning = classification.get('reasoning', '')
                            email.processing_status = 'completed'
                            email.is_classified = True
                            email.classified_at = datetime.now()
                            email.classification_model = openai_service.model
                            classified_count += 1
                
                # Commit classification updates
                db.session.commit()
                
                # Generate classification stats
                classification_results = openai_service.get_classification_stats(classifications)
                
                logger.info(f"Successfully classified {classified_count} emails")
                
            except Exception as e:
                logger.error(f"Error during email classification: {str(e)}")
                # Continue without classification - emails are still synced
        
        response_data = {
            'success': True,
            'message': f'Successfully synced {synced_count} new emails',
            'synced': synced_count,
            'skipped': skipped_count,
            'total_fetched': len(emails_data['value']),
            'classified': classified_count,
            'classification_enabled': classify_immediately
        }
        
        # Add classification stats if available
        if classification_results:
            response_data['classification_stats'] = classification_results
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error syncing emails: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Email synchronization failed'
        }), 500

@emails_bp.route('/', methods=['GET'])
@jwt_required()
def get_emails():
    """Get user's emails with filtering and pagination."""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 200)
        urgency = request.args.get('urgency')
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        
        # Get user's email accounts first
        user_email_accounts = EmailAccount.query.filter_by(user_id=user_id).all()
        account_ids = [account.id for account in user_email_accounts]
        
        if not account_ids:
            return jsonify({
                'success': True,
                'emails': [],
                'pagination': {
                    'page': 1,
                    'pages': 0,
                    'per_page': per_page,
                    'total': 0,
                    'has_next': False,
                    'has_prev': False
                }
            })
        
        # Build query for emails from user's accounts (exclude replied emails)
        query = Email.query.filter(
            Email.email_account_id.in_(account_ids),
            Email.processing_status != 'replied'  # Don't show emails that have been replied to
        )
        
        if urgency:
            query = query.filter(Email.urgency_category == urgency)
        
        if status:
            query = query.filter(Email.processing_status == status)
        
        if search:
            query = query.filter(
                db.or_(
                    Email.subject.ilike(f'%{search}%'),
                    Email.sender_name.ilike(f'%{search}%'),
                    Email.sender_email.ilike(f'%{search}%'),
                    Email.body_preview.ilike(f'%{search}%')
                )
            )
        
        # Order by received date (newest first)
        query = query.order_by(Email.received_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        emails = []
        for email in pagination.items:
            emails.append({
                'id': str(email.id),
                'subject': email.subject,
                'sender': {
                    'name': email.sender_name,
                    'email': email.sender_email
                },
                'preview': email.body_preview,
                'body_content': email.body_content,  # Add full content
                'body_preview': email.body_preview,  # Keep preview for compatibility
                'received_at': email.received_at.isoformat(),
                'is_read': email.is_read,
                'has_attachments': email.has_attachments,
                'urgency_category': email.urgency_category,
                'priority_level': email.priority_level,
                'ai_confidence': email.ai_confidence,
                'processing_status': email.processing_status,
                'ai_classification_reason': email.ai_reasoning
            })
        
        return jsonify({
            'success': True,
            'emails': emails,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting emails: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve emails'
        }), 500

@emails_bp.route('/<email_id>', methods=['GET'])
@jwt_required()
def get_email_detail(email_id):
    """Get detailed email information."""
    try:
        user_id = get_jwt_identity()
        
        # Get user's email accounts first
        user_email_accounts = EmailAccount.query.filter_by(user_id=user_id).all()
        account_ids = [account.id for account in user_email_accounts]
        
        email = Email.query.filter(
            Email.id == email_id,
            Email.email_account_id.in_(account_ids)
        ).first()
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email not found'
            }), 404
        
        return jsonify({
            'success': True,
            'email': {
                'id': str(email.id),
                'subject': email.subject,
                'sender': {
                    'name': email.sender_name,
                    'email': email.sender_email
                },
                'recipient': email.recipient_emails,
                'body_content': email.body_content,
                'body_preview': email.body_preview,
                'received_at': email.received_at.isoformat(),
                'is_read': email.is_read,
                'has_attachments': email.has_attachments,
                'is_important': email.is_important,
                'urgency_category': email.urgency_category,
                'priority_level': email.priority_level,
                'ai_confidence': email.ai_confidence,
                'processing_status': email.processing_status,
                'ai_classification_reason': email.ai_reasoning,
                'created_at': email.created_at.isoformat(),
                'updated_at': email.updated_at.isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting email detail: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve email details'
        }), 500

@emails_bp.route('/<email_id>/mark-read', methods=['POST'])
@jwt_required()
def mark_email_read(email_id):
    """Mark email as read both locally and in Microsoft."""
    try:
        user_id = get_jwt_identity()
        
        # Get user's email accounts first
        user_email_accounts = EmailAccount.query.filter_by(user_id=user_id).all()
        account_ids = [account.id for account in user_email_accounts]
        
        email = Email.query.filter(
            Email.id == email_id,
            Email.email_account_id.in_(account_ids)
        ).first()
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email not found'
            }), 404
        
        # Get email account for Microsoft Graph access
        email_account = EmailAccount.query.filter_by(
            id=email.email_account_id,
            is_active=True
        ).first()
        
        # Mark as read in Microsoft Graph first
        microsoft_success = False
        if email_account and email.microsoft_email_id and email_account.access_token:
            try:
                service = MicrosoftGraphService()
                microsoft_success = service.mark_email_as_read(
                    email_account.access_token,
                    email.microsoft_email_id
                )
                logger.info(f"Microsoft Graph mark as read result: {microsoft_success}")
            except Exception as e:
                logger.warning(f"Failed to mark email as read in Microsoft: {str(e)}")
                # Continue with local update even if Microsoft fails
        
        # Update local record
        email.is_read = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Email marked as read',
            'microsoft_updated': microsoft_success,
            'local_updated': True
        })
    
    except Exception as e:
        logger.error(f"Error marking email as read: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to mark email as read'
        }), 500

@emails_bp.route('/sync-status', methods=['GET', 'POST'])
@jwt_required()
def sync_email_statuses():
    """Sync read/unread status of all emails with Microsoft Graph."""
    try:
        user_id = get_jwt_identity()
        
        # Get user's email accounts
        email_account = EmailAccount.query.filter_by(
            user_id=user_id,
            provider='microsoft',
            is_active=True
        ).first()
        
        if not email_account or not email_account.access_token:
            return jsonify({
                'success': False,
                'error': 'Microsoft account not connected'
            }), 400
        
        # Handle both GET and POST requests
        if request.method == 'GET':
            # For GET requests, just return status without syncing
            return jsonify({
                'success': True,
                'message': 'Sync status endpoint available',
                'account_connected': True
            })
        
        # For POST requests, perform actual sync
        # Get parameters
        data = request.get_json() or {}
        limit = min(data.get('limit', 100), 200)  # Max 200 emails
        
        service = MicrosoftGraphService()
        
        # Fetch recent emails from Microsoft to sync status
        emails_data = service.get_user_emails(
            email_account.access_token,
            top=limit,
            folder='inbox'
        )
        
        if not emails_data or 'value' not in emails_data:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch emails from Microsoft'
            }), 400
        
        updated_count = 0
        processed_count = 0
        
        for email_data in emails_data['value']:
            processed_count += 1
            microsoft_id = email_data['id']
            current_is_read = email_data.get('isRead', False)
            
            # Find local email
            local_email = Email.query.filter_by(
                microsoft_email_id=microsoft_id,
                email_account_id=email_account.id
            ).first()
            
            if local_email and local_email.is_read != current_is_read:
                local_email.is_read = current_is_read
                local_email.updated_at = datetime.now()
                db.session.add(local_email)
                updated_count += 1
                logger.info(f"Synced read status for email {local_email.id}: {current_is_read}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Synchronized {updated_count} email statuses',
            'updated_count': updated_count,
            'processed_count': processed_count
        })
    
    except Exception as e:
        logger.error(f"Error syncing email statuses: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to sync email statuses'
        }), 500

@emails_bp.route('/<email_id>/update-urgency', methods=['POST'])
@jwt_required()
def update_email_urgency(email_id):
    """Update email urgency category."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'urgency_category' not in data:
            return jsonify({
                'success': False,
                'error': 'Urgency category is required'
            }), 400
        
        urgency_category = data['urgency_category']
        valid_urgencies = ['urgent', 'high', 'medium', 'low', 'processed']
        
        if urgency_category not in valid_urgencies:
            return jsonify({
                'success': False,
                'error': f'Invalid urgency category. Must be one of: {", ".join(valid_urgencies)}'
            }), 400
        
        # Get user's email accounts first
        user_email_accounts = EmailAccount.query.filter_by(user_id=user_id).all()
        account_ids = [account.id for account in user_email_accounts]
        
        email = Email.query.filter(
            Email.id == email_id,
            Email.email_account_id.in_(account_ids)
        ).first()
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email not found'
            }), 404
        
        # Update urgency
        email.urgency_category = urgency_category
        email.priority_level = get_priority_from_urgency(urgency_category)
        
        # If moving to processed, mark as read
        if urgency_category == 'processed':
            email.is_read = True
            email.processing_status = 'processed'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Email urgency updated successfully',
            'email': {
                'id': str(email.id),
                'urgency_category': email.urgency_category,
                'priority_level': email.priority_level,
                'processing_status': email.processing_status
            }
        })
    
    except Exception as e:
        logger.error(f"Error updating email urgency: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update email urgency'
        }), 500

@emails_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_email_stats():
    """Get email statistics for dashboard."""
    try:
        user_id = get_jwt_identity()
        
        # Get user's email accounts first
        user_email_accounts = EmailAccount.query.filter_by(user_id=user_id).all()
        account_ids = [account.id for account in user_email_accounts]
        
        if not account_ids:
            return jsonify({
                'success': True,
                'stats': {
                    'total_emails': 0,
                    'unread_emails': 0,
                    'by_urgency': {'urgent': 0, 'high': 0, 'medium': 0, 'low': 0, 'processed': 0},
                    'by_status': {'pending': 0, 'processing': 0, 'classified': 0, 'processed': 0}
                }
            })
        
        # Total emails
        total_emails = Email.query.filter(Email.email_account_id.in_(account_ids)).count()
        
        # Unread emails
        unread_emails = Email.query.filter(
            Email.email_account_id.in_(account_ids),
            Email.is_read == False
        ).count()
        
        # Emails by urgency
        urgency_stats = {}
        urgencies = ['urgent', 'high', 'medium', 'low', 'processed']
        
        for urgency in urgencies:
            count = Email.query.filter(
                Email.email_account_id.in_(account_ids),
                Email.urgency_category == urgency
            ).count()
            urgency_stats[urgency] = count
        
        # Processing status stats
        status_stats = {}
        statuses = ['pending', 'processing', 'classified', 'processed']
        
        for status in statuses:
            count = Email.query.filter(
                Email.email_account_id.in_(account_ids),
                Email.processing_status == status
            ).count()
            status_stats[status] = count
        
        return jsonify({
            'success': True,
            'stats': {
                'total_emails': total_emails,
                'unread_emails': unread_emails,
                'by_urgency': urgency_stats,
                'by_status': status_stats
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting email stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get email statistics'
        }), 500

@emails_bp.route('/send', methods=['POST'])
@jwt_required()
def send_email():
    """Send a new email via Microsoft Graph."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['to_email', 'subject', 'body']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        # Get email account
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
        
        logger.info(f"Attempting to send email to {data['to_email']}")
        logger.info(f"Email subject: {data['subject']}")
        
        # Send email via Microsoft Graph
        success = service.send_email(
            access_token=email_account.access_token,
            to_email=data['to_email'],
            subject=data['subject'],
            body=data['body']
        )
        
        logger.info(f"Send email result: {success}")
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Email sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send email'
            }), 500
    
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to send email'
        }), 500

@emails_bp.route('/<email_id>/reply', methods=['POST'])
@jwt_required()
def reply_to_email(email_id):
    """Reply to a specific email."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('body'):
            return jsonify({
                'success': False,
                'error': 'Reply body is required'
            }), 400
        
        # Get user's email accounts first
        user_email_accounts = EmailAccount.query.filter_by(user_id=user_id).all()
        account_ids = [account.id for account in user_email_accounts]
        
        # Get the original email
        email = Email.query.filter(
            Email.id == email_id,
            Email.email_account_id.in_(account_ids)
        ).first()
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Original email not found'
            }), 404
        
        # Get email account
        email_account = EmailAccount.query.filter_by(
            id=email.email_account_id,
            is_active=True
        ).first()
        
        if not email_account:
            return jsonify({
                'success': False,
                'error': 'Email account not found'
            }), 400
        
        service = MicrosoftGraphService()
        
        # Prepare reply subject (add "RE:" if not present)
        reply_subject = email.subject
        if not reply_subject.lower().startswith('re:'):
            reply_subject = f"RE: {reply_subject}"
        
        # Send reply via Microsoft Graph
        logger.info(f"Attempting to send reply to {email.sender_email}")
        logger.info(f"Reply subject: {reply_subject}")
        logger.info(f"Original email ID: {email.microsoft_email_id}")
        
        success = service.send_email(
            access_token=email_account.access_token,
            to_email=email.sender_email,
            subject=reply_subject,
            body=data['body'],
            reply_to_message_id=email.microsoft_email_id
        )
        
        logger.info(f"Send email result: {success}")
        
        if success:
            # Mark original email as read and hidden (replied to)
            email.is_read = True
            email.processing_status = 'replied'  # Different status so it doesn't appear in dashboard
            # Don't change urgency_category to 'processed' to avoid showing in processed column

            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Reply sent successfully',
                'email_updated': {
                    'id': str(email.id),
                    'processing_status': email.processing_status,
                    'urgency_category': email.urgency_category
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send reply'
            }), 500
    
    except Exception as e:
        logger.error(f"Error replying to email: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to send reply'
        }), 500

@emails_bp.route('/test-send', methods=['POST'])
@jwt_required()
def test_send_email():
    """Test endpoint to send a simple email for debugging."""
    try:
        user_id = get_jwt_identity()
        
        # Get email account
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
        
        # Send test email to yourself
        test_email = email_account.email_address
        test_subject = "Test Email from Email Manager IA - Debug"
        test_body = "<p>This is a test email to verify send functionality.</p><p>If you receive this, the send functionality is working correctly.</p>"
        
        logger.info(f"Testing email send to {test_email}")
        
        success = service.send_email(
            access_token=email_account.access_token,
            to_email=test_email,
            subject=test_subject,
            body=test_body
        )
        
        logger.info(f"Test email send result: {success}")
        
        return jsonify({
            'success': success,
            'message': 'Test email sent successfully' if success else 'Failed to send test email',
            'test_email': test_email
        })
    
    except Exception as e:
        logger.error(f"Error testing email send: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to test email send'
        }), 500

@emails_bp.route('/search', methods=['GET'])
@jwt_required()
def search_emails():
    """Search emails using Microsoft Graph search."""
    try:
        user_id = get_jwt_identity()
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        # Get email account
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
        
        # Search emails via Microsoft Graph
        search_results = service.search_emails(
            email_account.access_token,
            query,
            top=25
        )
        
        if not search_results or 'value' not in search_results:
            return jsonify({
                'success': False,
                'error': 'Search failed'
            }), 400
        
        # Format search results
        emails = []
        for email_data in search_results['value']:
            emails.append({
                'id': email_data['id'],
                'subject': email_data.get('subject', ''),
                'sender': {
                    'name': email_data.get('from', {}).get('emailAddress', {}).get('name', ''),
                    'email': email_data.get('from', {}).get('emailAddress', {}).get('address', '')
                },
                'preview': extract_email_preview(
                    email_data.get('body', {}).get('content', ''),
                    max_length=200
                ),
                'received_at': email_data.get('receivedDateTime', ''),
                'is_read': email_data.get('isRead', False),
                'has_attachments': email_data.get('hasAttachments', False)
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'results': emails,
            'total_found': len(emails)
        })
    
    except Exception as e:
        logger.error(f"Error searching emails: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Email search failed'
        }), 500

@emails_bp.route('/classify', methods=['POST'])
@jwt_required()
def classify_emails():
    """Classify specific emails or all pending emails using OpenAI."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Get email IDs to classify (or classify all pending if none specified)
        email_ids = data.get('email_ids', [])
        classify_all_pending = data.get('classify_all_pending', False)
        force_reclassify = data.get('force_reclassify', False)
        
        if not email_ids and not classify_all_pending:
            return jsonify({
                'success': False,
                'error': 'Must specify email_ids or set classify_all_pending=true'
            }), 400
        
        # Get user's email accounts first
        user_email_accounts = EmailAccount.query.filter_by(user_id=user_id).all()
        account_ids = [account.id for account in user_email_accounts]
        
        if not account_ids:
            return jsonify({
                'success': True,
                'message': 'No email accounts found',
                'classified': 0
            })
        
        # Build query for emails to classify
        query = Email.query.filter(Email.email_account_id.in_(account_ids))
        
        if email_ids:
            query = query.filter(Email.id.in_(email_ids))
        elif classify_all_pending:
            if force_reclassify:
                # Classify all emails
                query = query
            else:
                # Only classify pending emails
                query = query.filter(Email.processing_status == 'pending')
        
        emails = query.all()
        
        if not emails:
            return jsonify({
                'success': True,
                'message': 'No emails found to classify',
                'classified': 0
            })
        
        # Prepare email data for OpenAI
        emails_data = []
        for email in emails:
            emails_data.append({
                'email_id': str(email.id),
                'subject': email.subject,
                'sender_name': email.sender_name,
                'sender_email': email.sender_email,
                'body_preview': email.body_preview,
                'received_at': email.received_at.isoformat()
            })
        
        # Classify with OpenAI
        openai_service = OpenAIService()
        logger.info(f"Classifying {len(emails)} emails with OpenAI")
        
        classifications = openai_service.classify_batch(emails_data, batch_size=5)
        
        # Update emails with classification results
        classified_count = 0
        for i, email in enumerate(emails):
            if i < len(classifications):
                classification = classifications[i]
                
                email.urgency_category = classification.get('urgency_category', 'medium')
                email.priority_level = get_priority_from_urgency(email.urgency_category)
                email.ai_confidence = classification.get('confidence_score', 0.0)
                email.ai_reasoning = classification.get('reasoning', '')
                email.processing_status = 'classified'
                email.is_classified = True
                email.classified_at = datetime.now()
                email.classification_model = openai_service.model
                
                classified_count += 1
        
        db.session.commit()
        
        # Generate classification stats
        classification_stats = openai_service.get_classification_stats(classifications)
        
        return jsonify({
            'success': True,
            'message': f'Successfully classified {classified_count} emails',
            'classified': classified_count,
            'total_processed': len(emails),
            'classification_stats': classification_stats
        })
    
    except Exception as e:
        logger.error(f"Error classifying emails: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Email classification failed'
        }), 500

@emails_bp.route('/ai-status', methods=['GET'])
@jwt_required()
def get_ai_status():
    """Get AI service status and configuration."""
    try:
        from app.services.openai_service import OpenAIService
        
        openai_service = OpenAIService()
        status = openai_service.get_status()
        
        return jsonify({
            'success': True,
            'ai_service': status,
            'message': 'AI service status retrieved successfully'
        })
    
    except Exception as e:
        logger.error(f"Error getting AI status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get AI service status'
        }), 500

@emails_bp.route('/<email_id>/classify', methods=['POST'])
@jwt_required()
def classify_single_email(email_id):
    """Classify a single email using OpenAI."""
    try:
        user_id = get_jwt_identity()
        
        # Get user's email accounts first
        user_email_accounts = EmailAccount.query.filter_by(user_id=user_id).all()
        account_ids = [account.id for account in user_email_accounts]
        
        email = Email.query.filter(
            Email.id == email_id,
            Email.email_account_id.in_(account_ids)
        ).first()
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email not found'
            }), 404
        
        # Prepare email data
        email_data = {
            'subject': email.subject,
            'sender_name': email.sender_name,
            'sender_email': email.sender_email,
            'body_preview': email.body_preview,
            'received_at': email.received_at.isoformat()
        }
        
        # Classify with OpenAI
        openai_service = OpenAIService()
        classification = openai_service.classify_email(email_data)
        
        # Update email
        email.urgency_category = classification.get('urgency_category', 'medium')
        email.priority_level = get_priority_from_urgency(email.urgency_category)
        email.ai_confidence = classification.get('confidence_score', 0.0)
        email.ai_reasoning = classification.get('reasoning', '')
        email.processing_status = 'classified'
        email.is_classified = True
        email.classified_at = datetime.now()
        email.classification_model = openai_service.model
        
        db.session.commit()
        
        # Get response priority suggestion
        priority_suggestion = openai_service.suggest_response_priority(classification)
        
        return jsonify({
            'success': True,
            'message': 'Email classified successfully',
            'email': {
                'id': str(email.id),
                'urgency_category': email.urgency_category,
                'priority_level': email.priority_level,
                'ai_confidence': email.ai_confidence,
                'reasoning': email.ai_reasoning
            },
            'classification': classification,
            'priority_suggestion': priority_suggestion
        })
    
    except Exception as e:
        logger.error(f"Error classifying email {email_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Email classification failed'
        }), 500

@emails_bp.route('/classification-stats', methods=['GET'])
@jwt_required()
def get_classification_stats():
    """Get overall classification statistics for user's emails."""
    try:
        user_id = get_jwt_identity()
        
        # Get user's email accounts first
        user_email_accounts = EmailAccount.query.filter_by(user_id=user_id).all()
        account_ids = [account.id for account in user_email_accounts]
        
        if not account_ids:
            return jsonify({
                'success': True,
                'message': 'No email accounts found',
                'stats': {}
            })
        
        # Get all classified emails
        emails = Email.query.filter(
            Email.email_account_id.in_(account_ids),
            Email.processing_status == 'classified'
        ).all()
        
        if not emails:
            return jsonify({
                'success': True,
                'message': 'No classified emails found',
                'stats': {}
            })
        
        # Convert to format for stats calculation
        classifications = []
        for email in emails:
            classifications.append({
                'urgency_category': email.urgency_category,
                'ai_confidence': email.ai_confidence,
                'sender_type': 'externo',  # Would need to store this in DB
                'email_type': 'academico',  # Would need to store this in DB
                'requires_immediate_action': email.urgency_category in ['urgent', 'high']
            })
        
        # Generate stats
        openai_service = OpenAIService()
        stats = openai_service.get_classification_stats(classifications)
        
        # Add timing stats
        recent_emails = Email.query.filter(
            Email.email_account_id.in_(account_ids),
            Email.processing_status == 'classified',
            Email.created_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        stats['recent_classified'] = recent_emails
        stats['total_emails'] = Email.query.filter(Email.email_account_id.in_(account_ids)).count()
        stats['classification_coverage'] = round((len(emails) / stats['total_emails']) * 100, 1) if stats['total_emails'] > 0 else 0
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    
    except Exception as e:
        logger.error(f"Error getting classification stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get classification statistics'
        }), 500

@emails_bp.route('/openai-status', methods=['GET'])
@jwt_required()
def get_openai_status():
    """Get OpenAI service status and configuration."""
    try:
        openai_service = OpenAIService()
        status = openai_service.get_status()
        
        # Add some usage stats if available
        user_id = get_jwt_identity()
        # Get user's email accounts first
        user_email_accounts = EmailAccount.query.filter_by(user_id=user_id).all()
        account_ids = [account.id for account in user_email_accounts]
        
        if not account_ids:
            pending_count = 0
            classified_count = 0
        else:
            pending_count = Email.query.filter(
                Email.email_account_id.in_(account_ids),
                Email.processing_status == 'pending'
            ).count()
            
            classified_count = Email.query.filter(
                Email.email_account_id.in_(account_ids),
                Email.processing_status == 'classified'
            ).count()
        
        status['user_stats'] = {
            'pending_classification': pending_count,
            'already_classified': classified_count,
            'total_emails': pending_count + classified_count
        }
        
        return jsonify({
            'success': True,
            'openai_status': status
        })
    
    except Exception as e:
        logger.error(f"Error getting OpenAI status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get OpenAI status'
        }), 500

@emails_bp.route('/sent', methods=['GET'])
@jwt_required()
def get_sent_emails():
    """Get user's sent emails from Microsoft Graph SentItems folder."""
    try:
        user_id = get_jwt_identity()

        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 200)

        # Get email account
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

        # Check if we have a valid access token
        if not email_account.access_token:
            return jsonify({
                'success': False,
                'error': 'No access token available. Please reconnect your Microsoft account.'
            }), 401

        service = MicrosoftGraphService()

        # Fetch sent emails from Microsoft Graph SentItems folder
        emails_data = service.get_user_emails(
            email_account.access_token,
            top=per_page,
            folder='sentitems'  # This is the SentItems folder
        )

        if not emails_data:
            logger.error(f"Failed to fetch sent emails - likely token expired for user {user_id}")
            return jsonify({
                'success': False,
                'error': 'Failed to fetch sent emails from Microsoft. Token may have expired. Please reconnect your account.'
            }), 401

        if 'value' not in emails_data:
            logger.error(f"Unexpected response format from Microsoft Graph: {emails_data}")
            return jsonify({
                'success': False,
                'error': 'Unexpected response format from Microsoft Graph'
            }), 400

        # Format sent emails for frontend
        sent_emails = []
        for email_data in emails_data['value']:
            # Extract recipient information
            recipients = email_data.get('toRecipients', [])
            recipient_names = []
            recipient_emails = []

            for recipient in recipients:
                email_addr = recipient.get('emailAddress', {})
                name = email_addr.get('name', '')
                email = email_addr.get('address', '')
                if name:
                    recipient_names.append(name)
                if email:
                    recipient_emails.append(email)

            # Format recipient display (like Outlook shows)
            recipient_display = '; '.join(recipient_names) if recipient_names else '; '.join(recipient_emails)

            # Extract email preview
            body_preview = extract_email_preview(
                email_data.get('body', {}).get('content', ''),
                max_length=200
            )

            # Determine if this is a reply or a new email
            subject = email_data.get('subject', '')
            is_reply = (
                subject.lower().startswith('re:') or
                subject.lower().startswith('resp:') or
                subject.lower().startswith('respuesta:') or
                'conversationId' in email_data  # Microsoft Graph conversation threading
            )

            email_type = 'reply' if is_reply else 'sent'

            sent_emails.append({
                'id': email_data['id'],
                'subject': subject,
                'recipient': {
                    'name': recipient_display,  # This is what shows in "To" field
                    'emails': recipient_emails
                },
                'preview': body_preview,
                'body_content': email_data.get('body', {}).get('content', ''),
                'sent_at': email_data.get('sentDateTime', ''),
                'has_attachments': email_data.get('hasAttachments', False),
                'email_type': email_type,  # 'sent' or 'reply'
                'is_reply': is_reply
            })

        return jsonify({
            'success': True,
            'emails': sent_emails,
            'total_found': len(sent_emails),
            'message': f'Retrieved {len(sent_emails)} sent emails'
        })

    except Exception as e:
        logger.error(f"Error getting sent emails: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve sent emails'
        }), 500