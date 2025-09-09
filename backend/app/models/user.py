import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app import db

class User(db.Model):
    """User model for storing user information."""
    
    __tablename__ = 'users'
    
    # Primary key using string (for SQLite compatibility)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User information
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Microsoft Graph specific fields
    microsoft_user_id = Column(String(255), unique=True, nullable=True, index=True)
    profile_picture_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    email_accounts = relationship('EmailAccount', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        """Convert user object to dictionary for JSON serialization."""
        return {
            'id': str(self.id),
            'email': self.email,
            'name': self.full_name,
            'is_active': self.is_active,
            'microsoft_user_id': self.microsoft_user_id,
            'profile_picture_url': self.profile_picture_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email address."""
        return cls.query.filter_by(email=email, is_active=True).first()
    
    @classmethod
    def find_by_microsoft_id(cls, microsoft_user_id):
        """Find user by Microsoft user ID."""
        return cls.query.filter_by(microsoft_user_id=microsoft_user_id, is_active=True).first()
    
    def get_active_email_accounts(self):
        """Get all active email accounts for this user."""
        return [account for account in self.email_accounts if account.is_active]