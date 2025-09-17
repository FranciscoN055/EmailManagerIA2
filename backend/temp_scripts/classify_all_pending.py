#!/usr/bin/env python3
"""
Script para clasificar todos los correos pendientes
"""

import logging
from app import create_app
from app.models.email import Email
from app.services.openai_service import OpenAIService
from app.utils.helpers import get_priority_from_urgency
from app import db
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def classify_all_pending():
    """Clasificar todos los correos pendientes."""
    app = create_app()
    
    with app.app_context():
        # Obtener correos sin clasificar
        pending_emails = Email.query.filter_by(is_classified=False).all()
        
        logger.info(f"Encontrados {len(pending_emails)} correos sin clasificar")
        
        if not pending_emails:
            logger.info("No hay correos para clasificar")
            return
        
        # Preparar datos para clasificación
        emails_data = []
        for email in pending_emails:
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
        logger.info(f"Clasificando {len(emails_data)} correos con OpenAI...")
        
        try:
            # Clasificar en lotes de 5
            classifications = openai_service.classify_batch(emails_data, batch_size=5)
            
            # Actualizar correos con resultados
            classified_count = 0
            for i, email_data in enumerate(emails_data):
                if i < len(classifications):
                    classification = classifications[i]
                    
                    # Encontrar y actualizar el correo
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
                        
                        logger.info(f"Clasificado: {email.subject[:50]}... -> {email.urgency_category}")
            
            # Guardar cambios
            db.session.commit()
            logger.info(f"✅ Clasificación completada. {classified_count} correos actualizados.")
            
        except Exception as e:
            logger.error(f"❌ Error durante la clasificación: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    classify_all_pending()
