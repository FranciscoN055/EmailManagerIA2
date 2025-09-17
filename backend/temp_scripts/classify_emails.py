#!/usr/bin/env python3
"""
Script para clasificar todos los correos existentes con OpenAI
"""

from app import create_app
from app.models.email import Email
from app.services.openai_service import OpenAIService
from datetime import datetime

def classify_all_emails():
    """Clasificar todos los correos no clasificados."""
    app = create_app()
    
    with app.app_context():
        # Obtener todos los correos no clasificados
        unclassified_emails = Email.query.filter_by(is_classified=False).all()
        
        print(f"Encontrados {len(unclassified_emails)} correos sin clasificar")
        
        if not unclassified_emails:
            print("No hay correos para clasificar")
            return
        
        # Preparar datos para OpenAI
        emails_data = []
        for email in unclassified_emails:
            emails_data.append({
                'email_id': str(email.id),
                'subject': email.subject,
                'sender_name': email.sender_name,
                'sender_email': email.sender_email,
                'body_preview': email.body_preview,
                'received_at': email.received_at.isoformat()
            })
        
        # Clasificar con OpenAI
        openai_service = OpenAIService()
        print(f"Clasificando {len(emails_data)} correos con OpenAI...")
        
        try:
            classifications = openai_service.classify_batch(emails_data, batch_size=3)
            
            # Actualizar correos con resultados
            classified_count = 0
            for i, email in enumerate(unclassified_emails):
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
                    print(f"Clasificado: {email.subject[:50]}... -> {email.urgency_category}")
            
            # Guardar cambios
            from app import db
            db.session.commit()
            
            print(f"✅ Clasificados {classified_count} correos exitosamente")
            
        except Exception as e:
            print(f"❌ Error durante la clasificación: {str(e)}")

def get_priority_from_urgency(urgency):
    """Convertir urgencia a nivel de prioridad numérico."""
    priority_map = {
        'urgent': 1,
        'high': 2,
        'medium': 3,
        'low': 4
    }
    return priority_map.get(urgency, 3)

if __name__ == "__main__":
    classify_all_emails()
