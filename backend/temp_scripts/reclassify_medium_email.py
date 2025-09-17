#!/usr/bin/env python3
"""
Reclasificar el correo de cambio de horario que está en la base de datos
"""

from app import create_app
from app.models.email import Email
from app.services.openai_service import OpenAIService
from app.utils.helpers import get_priority_from_urgency
from app import db
from datetime import datetime

def reclassify_medium_email():
    """Reclasificar el correo de cambio de horario."""
    app = create_app()
    
    with app.app_context():
        # Buscar el correo de cambio de horario
        email = Email.query.filter(
            Email.subject.like('%cambio de horario%')
        ).first()
        
        if not email:
            print("❌ No se encontró el correo de cambio de horario")
            return
        
        print(f"=== RECLASIFICANDO CORREO ===")
        print(f"ID: {email.id}")
        print(f"Asunto: {email.subject}")
        print(f"Urgencia actual: {email.urgency_category}")
        print(f"Confianza actual: {email.ai_confidence}")
        print()
        
        # Preparar datos para reclasificación
        email_data = {
            'email_id': str(email.id),
            'subject': email.subject,
            'sender_name': email.sender_name,
            'sender_email': email.sender_email,
            'body_preview': email.body_preview,
            'received_at': email.received_at.isoformat()
        }
        
        # Clasificar con el nuevo prompt
        openai_service = OpenAIService()
        print("Clasificando con el nuevo prompt...")
        
        try:
            classification = openai_service.classify_email(email_data)
            
            print("✅ NUEVA CLASIFICACIÓN:")
            print(f"Urgencia: {classification['urgency_category']}")
            print(f"Confianza: {classification['confidence_score']}")
            print(f"Razonamiento: {classification['reasoning']}")
            
            # Actualizar el correo
            email.urgency_category = classification['urgency_category']
            email.priority_level = get_priority_from_urgency(email.urgency_category)
            email.ai_confidence = classification['confidence_score']
            email.ai_reasoning = classification['reasoning']
            email.processing_status = 'completed'
            email.is_classified = True
            email.classified_at = datetime.now()
            email.classification_model = openai_service.model
            
            # Guardar cambios
            db.session.commit()
            
            print(f"\n✅ Correo actualizado exitosamente")
            print(f"Nueva urgencia: {email.urgency_category}")
            print(f"Nueva prioridad: {email.priority_level}")
            
        except Exception as e:
            print(f"❌ Error durante la reclasificación: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    reclassify_medium_email()
