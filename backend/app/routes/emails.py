from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.microsoft_graph import MicrosoftGraphService
from app.services.email_processor import EmailProcessor
from app.models.user import User
from app.models.email import Email
from app.models.email_account import EmailAccount
from app.utils.helpers import extract_email_preview, get_priority_from_urgency
from app import db
from datetime import datetime
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
        
        # Get sync parameters
        data = request.get_json() or {}
        top = min(data.get('count', 50), 200)  # Max 200 emails per sync
        folder = data.get('folder', 'inbox')
        
        service = MicrosoftGraphService()
        
        # Fetch emails from Microsoft Graph
        emails_data = service.get_user_emails(
            email_account.access_token,
            top=top,
            folder=folder
        )
        
        if not emails_data or 'value' not in emails_data:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch emails from Microsoft'
            }), 400
        
        synced_count = 0
        skipped_count = 0
        
        for email_data in emails_data['value']:
            # Check if email already exists
            existing_email = Email.query.filter_by(
                microsoft_message_id=email_data['id']
            ).first()
            
            if existing_email:
                skipped_count += 1
                continue
            
            # Create new email record
            email = Email(
                user_id=user_id,
                email_account_id=email_account.id,
                microsoft_message_id=email_data['id'],
                subject=email_data.get('subject', ''),
                sender_email=email_data.get('from', {}).get('emailAddress', {}).get('address', ''),
                sender_name=email_data.get('from', {}).get('emailAddress', {}).get('name', ''),
                recipient_email=email_account.email_address,
                body_content=email_data.get('body', {}).get('content', ''),
                body_preview=extract_email_preview(
                    email_data.get('body', {}).get('content', ''),
                    max_length=500
                ),
                received_at=datetime.fromisoformat(
                    email_data['receivedDateTime'].replace('Z', '+00:00')
                ),
                is_read=email_data.get('isRead', False),
                has_attachments=email_data.get('hasAttachments', False),
                importance=email_data.get('importance', 'normal'),
                urgency_category='medium',  # Default, will be classified by AI
                priority_level=3,
                confidence_score=0.0,
                processing_status='pending'
            )
            
            db.session.add(email)
            synced_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully synced {synced_count} new emails',
            'synced': synced_count,
            'skipped': skipped_count,
            'total_fetched': len(emails_data['value'])
        })
    
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
        
        # Build query
        query = Email.query.filter_by(user_id=user_id)
        
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
                'received_at': email.received_at.isoformat(),
                'is_read': email.is_read,
                'has_attachments': email.has_attachments,
                'urgency_category': email.urgency_category,
                'priority_level': email.priority_level,
                'confidence_score': email.confidence_score,
                'processing_status': email.processing_status,
                'ai_classification_reason': email.ai_classification_reason
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
        
        email = Email.query.filter_by(
            id=email_id,
            user_id=user_id
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
                'recipient': email.recipient_email,
                'body_content': email.body_content,
                'body_preview': email.body_preview,
                'received_at': email.received_at.isoformat(),
                'is_read': email.is_read,
                'has_attachments': email.has_attachments,
                'importance': email.importance,
                'urgency_category': email.urgency_category,
                'priority_level': email.priority_level,
                'confidence_score': email.confidence_score,
                'processing_status': email.processing_status,
                'ai_classification_reason': email.ai_classification_reason,
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
        
        email = Email.query.filter_by(
            id=email_id,
            user_id=user_id
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
        
        if email_account and email.microsoft_message_id:
            service = MicrosoftGraphService()
            service.mark_email_as_read(
                email_account.access_token,
                email.microsoft_message_id
            )
        
        # Update local record
        email.is_read = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Email marked as read'
        })
    
    except Exception as e:
        logger.error(f"Error marking email as read: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to mark email as read'
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
        
        email = Email.query.filter_by(
            id=email_id,
            user_id=user_id
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
        
        # Total emails
        total_emails = Email.query.filter_by(user_id=user_id).count()
        
        # Unread emails
        unread_emails = Email.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
        
        # Emails by urgency
        urgency_stats = {}
        urgencies = ['urgent', 'high', 'medium', 'low', 'processed']
        
        for urgency in urgencies:
            count = Email.query.filter_by(
                user_id=user_id,
                urgency_category=urgency
            ).count()
            urgency_stats[urgency] = count
        
        # Processing status stats
        status_stats = {}
        statuses = ['pending', 'processing', 'classified', 'processed']
        
        for status in statuses:
            count = Email.query.filter_by(
                user_id=user_id,
                processing_status=status
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
        
        # Send email via Microsoft Graph
        success = service.send_email(
            access_token=email_account.access_token,
            to_email=data['to_email'],
            subject=data['subject'],
            body=data['body']
        )
        
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
        
        # Get the original email
        email = Email.query.filter_by(
            id=email_id,
            user_id=user_id
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
        success = service.send_email(
            access_token=email_account.access_token,
            to_email=email.sender_email,
            subject=reply_subject,
            body=data['body'],
            reply_to_message_id=email.microsoft_message_id
        )
        
        if success:
            # Mark original email as read and processed
            email.is_read = True
            email.processing_status = 'processed'
            if email.urgency_category not in ['processed']:
                email.urgency_category = 'processed'
                email.priority_level = 5
            
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