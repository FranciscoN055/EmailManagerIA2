#!/usr/bin/env python3
"""
Script de migración para reclasificar correos existentes con el nuevo prompt mejorado
Este script debe ejecutarse después de actualizar el código para mejorar la clasificación
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

def migrate_existing_emails():
    """
    Reclasificar todos los correos existentes con el nuevo prompt mejorado.
    Esto es útil cuando se actualiza el sistema de clasificación.
    """
    app = create_app()
    
    with app.app_context():
        # Obtener todos los correos clasificados
        all_emails = Email.query.filter_by(is_classified=True).all()
        
        logger.info(f"Encontrados {len(all_emails)} correos ya clasificados")
        
        if not all_emails:
            logger.info("No hay correos para migrar")
            return
        
        # Preparar datos para reclasificación
        emails_data = []
        for email in all_emails:
            emails_data.append({
                'email_id': str(email.id),
                'subject': email.subject,
                'sender_name': email.sender_name,
                'sender_email': email.sender_email,
                'body_preview': email.body_preview,
                'received_at': email.received_at.isoformat()
            })
        
        # Clasificar con el nuevo prompt mejorado
        openai_service = OpenAIService()
        logger.info(f"Reclasificando {len(emails_data)} correos con el nuevo prompt...")
        
        try:
            # Clasificar en lotes de 5 para evitar rate limiting
            batch_size = 5
            total_batches = (len(emails_data) + batch_size - 1) // batch_size
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(emails_data))
                batch_emails = emails_data[start_idx:end_idx]
                
                logger.info(f"Procesando lote {batch_num + 1}/{total_batches} ({len(batch_emails)} correos)")
                
                # Clasificar lote
                classifications = openai_service.classify_batch(batch_emails, batch_size=len(batch_emails))
                
                # Actualizar correos con nuevas clasificaciones
                for i, email_data in enumerate(batch_emails):
                    if i < len(classifications):
                        classification = classifications[i]
                        
                        # Encontrar y actualizar el correo
                        email = Email.query.get(email_data['email_id'])
                        if email:
                            old_urgency = email.urgency_category
                            old_confidence = email.ai_confidence
                            
                            # Actualizar con nueva clasificación
                            email.urgency_category = classification.get('urgency_category', 'medium')
                            email.priority_level = get_priority_from_urgency(email.urgency_category)
                            email.ai_confidence = classification.get('confidence_score', 0.0)
                            email.ai_reasoning = classification.get('reasoning', '')
                            email.processing_status = 'completed'
                            email.is_classified = True
                            email.classified_at = datetime.now()
                            email.classification_model = openai_service.model
                            
                            # Log del cambio
                            if old_urgency != email.urgency_category:
                                logger.info(f"Cambio: {email.subject[:50]}... {old_urgency} → {email.urgency_category} (confianza: {old_confidence:.2f} → {email.ai_confidence:.2f})")
                            else:
                                logger.info(f"Mantenido: {email.subject[:50]}... {email.urgency_category} (confianza: {old_confidence:.2f} → {email.ai_confidence:.2f})")
                
                # Guardar cambios del lote
                db.session.commit()
                logger.info(f"Lote {batch_num + 1} guardado exitosamente")
                
                # Pausa entre lotes para evitar rate limiting
                if batch_num < total_batches - 1:
                    logger.info("Esperando 10 segundos antes del siguiente lote...")
                    import time
                    time.sleep(10)
            
            logger.info(f"✅ Migración completada. {len(all_emails)} correos reclasificados exitosamente.")
            
            # Mostrar estadísticas finales
            show_final_stats()
            
        except Exception as e:
            logger.error(f"❌ Error durante la migración: {str(e)}")
            db.session.rollback()

def show_final_stats():
    """Mostrar estadísticas finales después de la migración."""
    app = create_app()
    
    with app.app_context():
        emails = Email.query.all()
        
        print(f"\n=== ESTADÍSTICAS FINALES ===")
        print(f"Total emails: {len(emails)}")
        print(f"Classified: {sum(1 for e in emails if e.is_classified)}")
        print()
        
        print(f"=== DISTRIBUCIÓN POR URGENCIA ===")
        print(f"Urgent: {sum(1 for e in emails if e.urgency_category == 'urgent')}")
        print(f"High: {sum(1 for e in emails if e.urgency_category == 'high')}")
        print(f"Medium: {sum(1 for e in emails if e.urgency_category == 'medium')}")
        print(f"Low: {sum(1 for e in emails if e.urgency_category == 'low')}")
        print()
        
        print(f"=== CORREOS URGENTES ===")
        urgent_emails = [e for e in emails if e.urgency_category == 'urgent']
        for email in urgent_emails:
            print(f"- {email.subject[:50]}... (Confidence: {email.ai_confidence})")
        
        print(f"\n=== CORREOS HIGH ===")
        high_emails = [e for e in emails if e.urgency_category == 'high']
        for email in high_emails:
            print(f"- {email.subject[:50]}... (Confidence: {email.ai_confidence})")
        
        print(f"\n=== CORREOS MEDIUM ===")
        medium_emails = [e for e in emails if e.urgency_category == 'medium']
        for email in medium_emails:
            print(f"- {email.subject[:50]}... (Confidence: {email.ai_confidence})")

if __name__ == "__main__":
    migrate_existing_emails()