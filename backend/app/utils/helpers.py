"""
Helper functions and utilities for the Email Manager IA application.
"""

import uuid
import re
from datetime import datetime, timezone
from email_validator import validate_email as email_validate, EmailNotValidError

def generate_uuid():
    """Generate a new UUID4."""
    return str(uuid.uuid4())

def format_datetime(dt, format_string='%Y-%m-%d %H:%M:%S UTC'):
    """Format datetime object to string."""
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.strftime(format_string)

def validate_email(email):
    """Validate email address format."""
    try:
        valid = email_validate(email)
        return True, valid.email
    except EmailNotValidError:
        return False, None

def sanitize_string(text, max_length=None):
    """Sanitize string input."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Apply max length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    return text

def extract_email_preview(body, max_length=500):
    """Extract a clean preview from email body."""
    if not body:
        return ""
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', body)
    
    # Remove excessive whitespace and newlines
    clean_text = re.sub(r'\s+', ' ', clean_text.strip())
    
    # Truncate if too long
    if len(clean_text) > max_length:
        clean_text = clean_text[:max_length-3] + "..."
    
    return clean_text

def get_urgency_from_priority(priority_level):
    """Convert priority level to urgency category."""
    priority_map = {
        1: 'urgent',
        2: 'high', 
        3: 'medium',
        4: 'low',
        5: 'processed'
    }
    return priority_map.get(priority_level, 'medium')

def get_priority_from_urgency(urgency_category):
    """Convert urgency category to priority level."""
    urgency_map = {
        'urgent': 1,
        'high': 2,
        'medium': 3,
        'low': 4,
        'processed': 5
    }
    return urgency_map.get(urgency_category, 3)

def calculate_confidence_color(confidence_score):
    """Get color code based on confidence score."""
    if confidence_score >= 0.9:
        return '#198754'  # Green
    elif confidence_score >= 0.7:
        return '#0078d4'  # Blue  
    elif confidence_score >= 0.5:
        return '#fd7e14'  # Orange
    else:
        return '#dc3545'  # Red