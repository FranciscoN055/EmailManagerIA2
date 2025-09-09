import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app import db

class EmailAccount(db.Model):
    """Email account model for storing Microsoft Graph connected accounts."""
    
    __tablename__ = 'email_accounts'
    
    # Primary key using string (for SQLite compatibility)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to User
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Account information
    email_address = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    provider = Column(String(50), default='microsoft', nullable=False)  # microsoft, gmail, etc.
    account_type = Column(String(50), default='outlook', nullable=False)  # outlook, exchange, etc.
    
    # Microsoft Graph tokens and authentication
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Sync status and configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    sync_enabled = Column(Boolean, default=True, nullable=False)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_status = Column(String(50), default='pending', nullable=False)  # pending, syncing, completed, error
    sync_error_message = Column(Text, nullable=True)
    
    # Email processing settings
    auto_classify_enabled = Column(Boolean, default=True, nullable=False)
    classification_prompt = Column(Text, nullable=True)  # Custom AI prompt if needed
    
    # Sync metadata
    total_emails_synced = Column(String(20), default='0', nullable=False)
    last_email_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='email_accounts')
    emails = relationship('Email', back_populates='email_account', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<EmailAccount {self.email_address}>'
    
    def to_dict(self):
        """Convert email account object to dictionary for JSON serialization."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'email_address': self.email_address,
            'display_name': self.display_name,
            'account_type': self.account_type,
            'is_active': self.is_active,
            'sync_enabled': self.sync_enabled,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'sync_status': self.sync_status,
            'sync_error_message': self.sync_error_message,
            'auto_classify_enabled': self.auto_classify_enabled,
            'total_emails_synced': self.total_emails_synced,
            'last_email_date': self.last_email_date.isoformat() if self.last_email_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_token_valid(self):
        """Check if the access token is still valid."""
        if not self.access_token or not self.token_expires_at:
            return False
        return datetime.now(timezone.utc) < self.token_expires_at
    
    def update_tokens(self, access_token, refresh_token=None, expires_in=3600):
        """Update authentication tokens."""
        self.access_token = access_token
        if refresh_token:
            self.refresh_token = refresh_token
        self.token_expires_at = datetime.now(timezone.utc).replace(microsecond=0) + \
                               timezone.timedelta(seconds=expires_in - 300)  # 5 min buffer
        db.session.commit()
    
    def update_sync_status(self, status, error_message=None):
        """Update sync status and timestamp."""
        self.sync_status = status
        self.sync_error_message = error_message
        if status == 'completed':
            self.last_sync_at = datetime.now(timezone.utc)
        db.session.commit()
    
    @classmethod
    def find_by_email_address(cls, email_address):
        """Find email account by email address."""
        return cls.query.filter_by(email_address=email_address, is_active=True).first()
    
    @classmethod
    def get_accounts_for_sync(cls):
        """Get all accounts that need to be synced."""
        return cls.query.filter_by(
            is_active=True,
            sync_enabled=True,
            sync_status='pending'
        ).all()
    
    def get_emails_by_urgency(self):
        """Get emails grouped by urgency level."""
        from .email import Email
        emails_by_urgency = {
            'urgent': [],
            'high': [],
            'medium': [],
            'low': [],
            'processed': []
        }
        
        for email in self.emails:
            if email.urgency_category in emails_by_urgency:
                emails_by_urgency[email.urgency_category].append(email.to_dict())
        
        return emails_by_urgency