import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, Float, JSON
from sqlalchemy.orm import relationship
from app import db

class Email(db.Model):
    """Email model for storing email data and AI classifications."""
    
    __tablename__ = 'emails'
    
    # Primary key using string (for SQLite compatibility)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to EmailAccount
    email_account_id = Column(String(36), ForeignKey('email_accounts.id', ondelete='CASCADE'), nullable=False)
    
    # Microsoft Graph email ID for sync purposes
    microsoft_email_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Email metadata
    subject = Column(Text, nullable=False)
    sender_name = Column(String(255), nullable=False)
    sender_email = Column(String(255), nullable=False, index=True)
    recipient_emails = Column(Text, nullable=True)  # JSON string of recipients
    
    # Email content
    body_preview = Column(Text, nullable=True)  # First 500 chars for preview
    body_content = Column(Text, nullable=True)  # Full email body
    has_attachments = Column(Boolean, default=False, nullable=False)
    attachment_count = Column(Integer, default=0, nullable=False)
    
    # Email timestamps
    received_at = Column(DateTime(timezone=True), nullable=False, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Email status
    is_read = Column(Boolean, default=False, nullable=False)
    is_starred = Column(Boolean, default=False, nullable=False)
    is_important = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    
    # AI Classification results
    priority_level = Column(Integer, default=3, nullable=False)  # 1=urgent, 2=high, 3=medium, 4=low, 5=processed
    urgency_category = Column(String(20), default='medium', nullable=False)  # urgent, high, medium, low, processed
    ai_confidence = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0 confidence score
    ai_reasoning = Column(Text, nullable=True)  # AI explanation for classification
    
    # Classification status
    is_classified = Column(Boolean, default=False, nullable=False)
    classified_at = Column(DateTime(timezone=True), nullable=True)
    classification_model = Column(String(50), nullable=True)  # e.g., 'gpt-4', 'gpt-3.5-turbo'
    
    # Custom tags and metadata
    custom_tags = Column(JSON, nullable=True)  # Custom tags as JSON array
    user_notes = Column(Text, nullable=True)  # User-added notes
    
    # Processing metadata
    processing_status = Column(String(50), default='pending', nullable=False)  # pending, processing, completed, error
    processing_error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    email_account = relationship('EmailAccount', back_populates='emails')
    
    def __repr__(self):
        return f'<Email {self.subject[:50]}...>'
    
    def to_dict(self):
        """Convert email object to dictionary for JSON serialization."""
        return {
            'id': str(self.id),
            'email_account_id': str(self.email_account_id),
            'microsoft_email_id': self.microsoft_email_id,
            'subject': self.subject,
            'sender': self.sender_name,
            'sender_email': self.sender_email,
            'recipient_emails': self.recipient_emails,
            'preview': self.body_preview,
            'body_content': self.body_content,
            'has_attachments': self.has_attachments,
            'attachment_count': self.attachment_count,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'is_read': self.is_read,
            'is_starred': self.is_starred,
            'is_important': self.is_important,
            'is_archived': self.is_archived,
            'priority_level': self.priority_level,
            'urgency_category': self.urgency_category,
            'ai_confidence': self.ai_confidence,
            'ai_reasoning': self.ai_reasoning,
            'is_classified': self.is_classified,
            'classified_at': self.classified_at.isoformat() if self.classified_at else None,
            'classification_model': self.classification_model,
            'custom_tags': self.custom_tags,
            'user_notes': self.user_notes,
            'processing_status': self.processing_status,
            'processing_error': self.processing_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def mark_as_read(self):
        """Mark email as read."""
        self.is_read = True
        db.session.commit()
    
    def toggle_star(self):
        """Toggle starred status."""
        self.is_starred = not self.is_starred
        db.session.commit()
    
    def archive(self):
        """Archive email and mark as processed."""
        self.is_archived = True
        self.urgency_category = 'processed'
        self.priority_level = 5
        db.session.commit()
    
    def update_classification(self, urgency_category, priority_level, confidence, reasoning, model_name):
        """Update AI classification results."""
        self.urgency_category = urgency_category
        self.priority_level = priority_level
        self.ai_confidence = confidence
        self.ai_reasoning = reasoning
        self.classification_model = model_name
        self.is_classified = True
        self.classified_at = datetime.now(timezone.utc)
        self.processing_status = 'completed'
        db.session.commit()
    
    @classmethod
    def find_by_microsoft_id(cls, microsoft_email_id):
        """Find email by Microsoft email ID."""
        return cls.query.filter_by(microsoft_email_id=microsoft_email_id).first()
    
    @classmethod
    def get_unclassified_emails(cls, limit=10):
        """Get emails that need AI classification."""
        return cls.query.filter_by(
            is_classified=False,
            processing_status='pending'
        ).order_by(cls.received_at.desc()).limit(limit).all()
    
    @classmethod
    def get_emails_by_urgency(cls, email_account_id, urgency_category):
        """Get emails by urgency category for a specific account."""
        return cls.query.filter_by(
            email_account_id=email_account_id,
            urgency_category=urgency_category,
            is_archived=False
        ).order_by(cls.received_at.desc()).all()
    
    @classmethod
    def get_recent_emails(cls, email_account_id, days=7, limit=50):
        """Get recent emails for an account."""
        cutoff_date = datetime.now(timezone.utc) - timezone.timedelta(days=days)
        return cls.query.filter(
            cls.email_account_id == email_account_id,
            cls.received_at >= cutoff_date,
            cls.is_archived == False
        ).order_by(cls.received_at.desc()).limit(limit).all()
    
    def get_time_until_urgent(self):
        """Calculate time until this email becomes urgent based on received time."""
        now = datetime.now(timezone.utc)
        time_diff = now - self.received_at
        
        # Business logic for urgency timing
        if time_diff.total_seconds() < 3600:  # Less than 1 hour
            return 'urgent'
        elif time_diff.total_seconds() < 10800:  # Less than 3 hours  
            return 'high'
        elif time_diff.days == 0:  # Same day
            return 'medium'
        elif time_diff.days == 1:  # Next day
            return 'low'
        else:
            return 'processed'