"""
Microsoft Graph API Service
Handles authentication and email synchronization with Microsoft Graph.
"""

import requests
import msal
from flask import current_app, url_for
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class MicrosoftGraphService:
    """Service class for Microsoft Graph API operations."""
    
    def __init__(self, config=None):
        self.config = config or current_app.config
        self.client_id = self.config.get('MICROSOFT_CLIENT_ID')
        self.client_secret = self.config.get('MICROSOFT_CLIENT_SECRET')
        self.tenant_id = self.config.get('MICROSOFT_TENANT_ID', 'common')
        self.redirect_uri = self.config.get('MICROSOFT_REDIRECT_URI')
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = [
            "https://graph.microsoft.com/Mail.ReadWrite", 
            "https://graph.microsoft.com/Mail.Send",
            "https://graph.microsoft.com/User.Read"
        ]
    
    def get_status(self):
        """Get service status."""
        return {
            'service': 'MicrosoftGraphService',
            'status': 'ready',
            'message': 'Microsoft Graph service configured and ready',
            'has_credentials': bool(self.client_id and self.client_secret)
        }
    
    def get_auth_url(self, state=None):
        """Generate Microsoft OAuth2 authorization URL."""
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
            
            auth_url = app.get_authorization_request_url(
                self.scopes,
                redirect_uri=self.redirect_uri,
                state=state
            )
            return auth_url
        except Exception as e:
            logger.error(f"Error generating auth URL: {str(e)}")
            return None
    
    def exchange_code_for_tokens(self, code):
        """Exchange authorization code for access and refresh tokens."""
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
            
            result = app.acquire_token_by_authorization_code(
                code,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            return result
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {str(e)}")
            return None
    
    def refresh_access_token(self, refresh_token):
        """Refresh access token using refresh token."""
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
            
            result = app.acquire_token_by_refresh_token(
                refresh_token,
                scopes=self.scopes
            )
            
            return result
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return None
    
    def get_user_profile(self, access_token):
        """Get user profile information from Microsoft Graph."""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting user profile: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return None
    
    def get_user_emails(self, access_token, top=50, skip=0, folder='inbox'):
        """Get user emails from Microsoft Graph."""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Build query parameters
        params = {
            '$top': top,
            '$skip': skip,
            '$orderby': 'receivedDateTime desc',
            '$select': 'id,subject,sender,from,toRecipients,receivedDateTime,createdDateTime,body,isRead,importance,flag,hasAttachments,internetMessageHeaders'
        }
        
        url = f'https://graph.microsoft.com/v1.0/me/mailFolders/{folder}/messages'
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting emails: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting emails: {str(e)}")
            return None
    
    def get_email_by_id(self, access_token, message_id):
        """Get specific email by ID."""
        headers = {'Authorization': f'Bearer {access_token}'}
        url = f'https://graph.microsoft.com/v1.0/me/messages/{message_id}'
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting email {message_id}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting email {message_id}: {str(e)}")
            return None
    
    def send_email(self, access_token, to_email, subject, body, reply_to_message_id=None):
        """Send email or reply to existing email."""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        email_data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body
                },
                "toRecipients": [{
                    "emailAddress": {
                        "address": to_email
                    }
                }]
            }
        }
        
        try:
            if reply_to_message_id:
                # Reply to specific message
                url = f'https://graph.microsoft.com/v1.0/me/messages/{reply_to_message_id}/reply'
                response = requests.post(url, headers=headers, json={"message": email_data["message"]}, timeout=10)
            else:
                # Send new email
                url = 'https://graph.microsoft.com/v1.0/me/sendMail'
                response = requests.post(url, headers=headers, json=email_data, timeout=10)
            
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def mark_email_as_read(self, access_token, message_id):
        """Mark email as read."""
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f'https://graph.microsoft.com/v1.0/me/messages/{message_id}'
        data = {"isRead": True}
        
        try:
            response = requests.patch(url, headers=headers, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error marking email as read: {str(e)}")
            return False
    
    def get_mail_folders(self, access_token):
        """Get user's mail folders."""
        headers = {'Authorization': f'Bearer {access_token}'}
        url = 'https://graph.microsoft.com/v1.0/me/mailFolders'
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting mail folders: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting mail folders: {str(e)}")
            return None
    
    def search_emails(self, access_token, query, top=25):
        """Search emails by query."""
        headers = {'Authorization': f'Bearer {access_token}'}
        
        params = {
            '$search': f'"{query}"',
            '$top': top,
            '$orderby': 'receivedDateTime desc'
        }
        
        url = 'https://graph.microsoft.com/v1.0/me/messages'
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error searching emails: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error searching emails: {str(e)}")
            return None