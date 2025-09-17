#!/usr/bin/env python3
"""
Script para verificar el estado de clasificación de correos
"""

from app import create_app
from app.models.email import Email

def check_classification():
    """Verificar el estado de clasificación de correos."""
    app = create_app()
    
    with app.app_context():
        emails = Email.query.all()
        print(f"=== VERIFICANDO {len(emails)} CORREOS ===")
        
        for i, email in enumerate(emails[-5:]):  # Últimos 5 correos
            print(f"\n--- Correo {i+1} ---")
            print(f"Subject: {email.subject[:60]}...")
            print(f"Classified: {email.is_classified}")
            print(f"Urgency: {email.urgency_category}")
            print(f"AI Confidence: {email.ai_confidence}")
            print(f"AI Reasoning: {email.ai_reasoning[:100]}...")
            print(f"Model: {email.classification_model}")
            print(f"Processing Status: {email.processing_status}")
            print(f"Classified At: {email.classified_at}")

if __name__ == "__main__":
    check_classification()
