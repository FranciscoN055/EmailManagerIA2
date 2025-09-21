#!/usr/bin/env python3
"""
Script para reclasificar correos específicos con deadlines que están mal clasificados
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.email import Email
from app.services.openai_service import GeminiService
from app import db
from datetime import datetime

def fix_deadline_emails():
    print("CORRIGIENDO CORREOS CON DEADLINES")
    print("=" * 50)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    app = create_app()
    with app.app_context():
        # Buscar los correos específicos con deadlines problemáticos
        problematic_subjects = [
            "Justificar inasistencia",
            "Cambio de sección Cálculo Multivariable",
            "Duda clase hoy"
        ]

        emails_to_fix = []
        for subject in problematic_subjects:
            email = Email.query.filter(Email.subject.like(f"%{subject}%")).first()
            if email and email.urgency_category == 'low':
                emails_to_fix.append(email)

        print(f"Encontrados {len(emails_to_fix)} correos para corregir:")
        for email in emails_to_fix:
            print(f"- {email.subject}")
        print()

        if not emails_to_fix:
            print("No se encontraron correos para corregir")
            return

        # Inicializar Gemini
        gemini_service = GeminiService()

        if not gemini_service.api_key:
            print("ERROR: No se encontró API Key de Gemini")
            return

        print("Reclasificando con prompt mejorado...")
        print("-" * 40)

        success_count = 0
        changes_count = 0

        for i, email in enumerate(emails_to_fix, 1):
            try:
                print(f"[{i}/{len(emails_to_fix)}] Procesando: {email.subject}")
                print(f"   Categoría actual: {email.urgency_category}")

                # Preparar datos del correo para Gemini
                email_data = {
                    'subject': email.subject or '',
                    'sender_email': email.sender_email or '',
                    'sender_name': email.sender_name or '',
                    'body_preview': email.body_preview or '',
                    'received_at': email.received_at.isoformat() if email.received_at else datetime.now().isoformat()
                }

                # Clasificar con Gemini (prompt mejorado)
                old_category = email.urgency_category
                result = gemini_service.classify_email(email_data)

                # Actualizar la categoría
                new_category = result.get('urgency_category', 'low')
                confidence = result.get('confidence_score', 0)
                reasoning = result.get('reasoning', '')

                email.urgency_category = new_category
                email.ai_confidence = confidence
                email.ai_reasoning = reasoning
                email.sender_type = result.get('sender_type', 'unknown')
                email.email_type = result.get('email_type', 'other')

                # Mostrar resultado
                if old_category != new_category:
                    print(f"   CAMBIO: {old_category} -> {new_category} (confianza: {confidence})")
                    print(f"   Nuevo razonamiento: {reasoning}")
                    changes_count += 1
                else:
                    print(f"   Sin cambio: {new_category} (confianza: {confidence})")
                    print(f"   Razonamiento: {reasoning}")

                success_count += 1
                print()

            except Exception as e:
                print(f"   ERROR: {str(e)}")
                continue

        # Guardar cambios en la base de datos
        try:
            db.session.commit()
            print("=" * 50)
            print("CORRECCIÓN COMPLETADA")
            print(f"Correos procesados: {success_count}")
            print(f"Correos con cambios: {changes_count}")
            print("Cambios guardados en la base de datos")
            print()

            if changes_count > 0:
                print("SUCCESS: Correos con deadlines reclasificados correctamente!")
                print("Ve al dashboard y actualiza para ver los cambios")
            else:
                print("INFO: No hubo cambios en las clasificaciones")

        except Exception as e:
            db.session.rollback()
            print(f"ERROR al guardar: {str(e)}")
            return False

        return True

def show_updated_summary():
    """Mostrar resumen actualizado"""
    app = create_app()
    with app.app_context():
        print("\nRESUMEN ACTUALIZADO:")
        print("-" * 30)

        categories = ['urgent', 'high', 'medium', 'low']
        for category in categories:
            count = Email.query.filter(Email.urgency_category == category).count()
            print(f"{category.upper():10}: {count} correos")

if __name__ == "__main__":
    print("Corrigiendo clasificación de correos con deadlines...")
    print()

    success = fix_deadline_emails()

    if success:
        show_updated_summary()
        print()
        print("SUCCESS: Corrección de deadlines completada!")
    else:
        print("ERROR: La corrección falló")