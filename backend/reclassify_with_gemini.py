#!/usr/bin/env python3
"""
Script para reclasificar todos los correos existentes usando Gemini
Mantiene los correos procesados intactos, solo reclasifica urgent/high/medium/low
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.email import Email
from app.services.openai_service import GeminiService
from app import db
from datetime import datetime

def reclassify_emails_with_gemini():
    print("RECLASIFICACIÓN CON GEMINI - Email Manager IA")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    app = create_app()
    with app.app_context():
        # Obtener todos los correos que NO están procesados
        emails_to_reclassify = Email.query.filter(
            Email.urgency_category.in_(['urgent', 'high', 'medium', 'low'])
        ).all()

        print(f"Encontrados {len(emails_to_reclassify)} correos para reclasificar")
        print("Categorías a reclasificar: urgent, high, medium, low")
        print("Los correos 'processed' se mantendrán intactos")
        print()

        if not emails_to_reclassify:
            print("No hay correos para reclasificar")
            return

        # Proceder automáticamente con la reclasificación
        print("Procediendo con la reclasificación automáticamente...")

        # Inicializar Gemini
        gemini_service = GeminiService()

        if not gemini_service.api_key:
            print("ERROR: No se encontró API Key de Gemini")
            return

        print("Iniciando reclasificación con Gemini...")
        print("-" * 40)

        success_count = 0
        error_count = 0
        changes_count = 0

        for i, email in enumerate(emails_to_reclassify, 1):
            try:
                print(f"[{i}/{len(emails_to_reclassify)}] Procesando: {email.subject[:50]}...")

                # Preparar datos del correo para Gemini
                email_data = {
                    'subject': email.subject or '',
                    'sender_email': email.sender_email or '',
                    'sender_name': email.sender_name or '',
                    'body_preview': email.body_preview or '',
                    'received_at': email.received_at.isoformat() if email.received_at else datetime.now().isoformat()
                }

                # Clasificar con Gemini
                old_category = email.urgency_category
                result = gemini_service.classify_email(email_data)

                # Actualizar la categoría
                new_category = result.get('urgency_category', 'low')
                confidence = result.get('confidence_score', 0)
                reasoning = result.get('reasoning', '')

                email.urgency_category = new_category
                email.confidence_score = confidence
                email.ai_reasoning = reasoning
                email.sender_type = result.get('sender_type', 'unknown')
                email.email_type = result.get('email_type', 'other')

                # Mostrar cambio si hubo uno
                if old_category != new_category:
                    print(f"   CAMBIO: {old_category} -> {new_category} (confianza: {confidence})")
                    changes_count += 1
                else:
                    print(f"   Sin cambio: {new_category} (confianza: {confidence})")

                success_count += 1

            except Exception as e:
                print(f"   ERROR: {str(e)}")
                error_count += 1
                continue

        # Guardar cambios en la base de datos
        try:
            db.session.commit()
            print()
            print("=" * 60)
            print("RECLASIFICACION COMPLETADA")
            print(f"Correos procesados exitosamente: {success_count}")
            print(f"Correos con cambios de categoria: {changes_count}")
            print(f"Errores: {error_count}")
            print("Cambios guardados en la base de datos")
            print()
            print("Ahora puedes actualizar el dashboard para ver los cambios")

        except Exception as e:
            db.session.rollback()
            print(f"ERROR al guardar en la base de datos: {str(e)}")
            return False

        return True

def show_category_summary():
    """Mostrar resumen de categorías después de la reclasificación"""
    app = create_app()
    with app.app_context():
        print("\nRESUMEN POR CATEGORÍAS:")
        print("-" * 30)

        categories = ['urgent', 'high', 'medium', 'low', 'processed']
        for category in categories:
            count = Email.query.filter(Email.urgency_category == category).count()
            print(f"{category.upper():10}: {count} correos")

if __name__ == "__main__":
    print("Iniciando reclasificación con Gemini...")
    print()

    # Mostrar resumen antes
    print("ESTADO ACTUAL:")
    show_category_summary()
    print()

    # Realizar reclasificación
    success = reclassify_emails_with_gemini()

    if success:
        # Mostrar resumen después
        print("ESTADO DESPUÉS DE RECLASIFICACIÓN:")
        show_category_summary()
        print()
        print("SUCCESS: Reclasificación completada exitosamente!")
        print("Ve al dashboard y actualiza para ver los cambios")
    else:
        print("ERROR: La reclasificación falló")