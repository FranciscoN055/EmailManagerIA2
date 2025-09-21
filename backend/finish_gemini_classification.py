#!/usr/bin/env python3
"""
Script para terminar la reclasificación de correos que quedaron pendientes
Solo procesa los correos que no tienen ai_reasoning (que cayeron al fallback)
"""

import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.email import Email
from app.services.openai_service import GeminiService
from app import db
from datetime import datetime

def finish_gemini_classification():
    print("COMPLETANDO CLASIFICACION CON GEMINI")
    print("=" * 50)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    app = create_app()
    with app.app_context():
        # Buscar correos que no tienen ai_reasoning (fueron clasificados por fallback)
        emails_pending = Email.query.filter(
            Email.urgency_category.in_(['urgent', 'high', 'medium', 'low']),
            (Email.ai_reasoning.is_(None) | (Email.ai_reasoning == ''))
        ).all()

        print(f"Encontrados {len(emails_pending)} correos pendientes de clasificacion Gemini")
        print("Solo se procesaran correos sin ai_reasoning (fallback)")
        print()

        if not emails_pending:
            print("Todos los correos ya fueron clasificados con Gemini!")
            return True

        # Inicializar Gemini
        gemini_service = GeminiService()

        if not gemini_service.api_key:
            print("ERROR: No se encontro API Key de Gemini")
            return False

        print("Continuando clasificacion con Gemini...")
        print("-" * 40)

        success_count = 0
        error_count = 0
        changes_count = 0

        for i, email in enumerate(emails_pending, 1):
            try:
                print(f"[{i}/{len(emails_pending)}] Procesando: {email.subject[:50]}...")

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

                # Actualizar la categoria
                new_category = result.get('urgency_category', 'low')
                confidence = result.get('confidence_score', 0)
                reasoning = result.get('reasoning', '')

                email.urgency_category = new_category
                email.confidence_score = confidence
                email.ai_reasoning = reasoning
                email.sender_type = result.get('sender_type', 'unknown')
                email.email_type = result.get('email_type', 'other')

                # Mostrar resultado
                if old_category != new_category:
                    print(f"   CAMBIO: {old_category} -> {new_category} (confianza: {confidence})")
                    changes_count += 1
                else:
                    print(f"   Sin cambio: {new_category} (confianza: {confidence})")

                success_count += 1

                # Pequena pausa para evitar rate limits
                time.sleep(0.1)

            except Exception as e:
                print(f"   ERROR: {str(e)}")
                error_count += 1
                continue

        # Guardar cambios en la base de datos
        try:
            db.session.commit()
            print()
            print("=" * 50)
            print("CLASIFICACION COMPLETADA")
            print(f"Correos procesados exitosamente: {success_count}")
            print(f"Correos con cambios de categoria: {changes_count}")
            print(f"Errores: {error_count}")
            print("Cambios guardados en la base de datos")
            print()
            print("Ahora TODOS los correos han sido clasificados con Gemini!")

        except Exception as e:
            db.session.rollback()
            print(f"ERROR al guardar en la base de datos: {str(e)}")
            return False

        return True

def show_final_summary():
    """Mostrar resumen final de todas las categorias"""
    app = create_app()
    with app.app_context():
        print("\nRESUMEN FINAL:")
        print("-" * 30)

        categories = ['urgent', 'high', 'medium', 'low', 'processed']
        total_gemini = 0

        for category in categories:
            count = Email.query.filter(Email.urgency_category == category).count()
            print(f"{category.upper():10}: {count} correos")
            if category != 'processed':
                total_gemini += count

        # Contar correos con ai_reasoning (clasificados por Gemini)
        gemini_classified = Email.query.filter(
            Email.urgency_category.in_(['urgent', 'high', 'medium', 'low']),
            Email.ai_reasoning.isnot(None),
            Email.ai_reasoning != ''
        ).count()

        print(f"\nClasificados con Gemini: {gemini_classified}/{total_gemini}")

        if gemini_classified == total_gemini:
            print("SUCCESS: Todos los correos clasificados con Gemini!")
        else:
            print(f"Pendientes: {total_gemini - gemini_classified} correos")

if __name__ == "__main__":
    print("Terminando clasificacion con Gemini...")
    print()

    # Realizar clasificacion pendiente
    success = finish_gemini_classification()

    if success:
        # Mostrar resumen final
        show_final_summary()
        print()
        print("SUCCESS: Clasificacion con Gemini completada!")
        print("Ve al dashboard y actualiza para ver todos los cambios")
    else:
        print("ERROR: La clasificacion fallo")