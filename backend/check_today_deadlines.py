#!/usr/bin/env python3
"""
Script para verificar correos con deadlines de hoy que están en prioridad baja
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.email import Email
from datetime import datetime

def check_today_deadlines():
    print("VERIFICANDO CORREOS CON DEADLINES HOY")
    print("=" * 50)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    app = create_app()
    with app.app_context():
        # Buscar correos de prioridad baja
        low_priority_emails = Email.query.filter(
            Email.urgency_category == 'low'
        ).all()

        print(f"Total correos en prioridad BAJA: {len(low_priority_emails)}")
        print()

        # Palabras clave que indican deadline hoy
        today_keywords = [
            'hoy', 'today', 'último día', 'ultimo dia', 'deadline',
            'vence hoy', 'para hoy', 'urgente hoy', 'debe ser hoy',
            'antes de las', 'hasta las', 'cierra hoy'
        ]

        suspicious_emails = []

        for email in low_priority_emails:
            email_text = (
                (email.subject or '') + ' ' +
                (email.body_preview or '') + ' ' +
                (email.ai_reasoning or '')
            ).lower()

            has_today_keyword = any(keyword in email_text for keyword in today_keywords)

            if has_today_keyword:
                suspicious_emails.append(email)

        print(f"Correos sospechosos (baja prioridad con keywords de HOY): {len(suspicious_emails)}")
        print()

        if suspicious_emails:
            print("CORREOS QUE DEBERÍAN SER REVISADOS:")
            print("-" * 40)

            for i, email in enumerate(suspicious_emails, 1):
                print(f"[{i}] ASUNTO: {email.subject}")
                print(f"    REMITENTE: {email.sender_email}")
                print(f"    PREVIEW: {email.body_preview[:100]}...")
                print(f"    CATEGORIA ACTUAL: {email.urgency_category}")
                print(f"    CONFIANZA: {email.ai_confidence}")
                print(f"    RAZONAMIENTO: {email.ai_reasoning}")
                print(f"    FECHA: {email.received_at}")
                print()

        # También verificar todos los correos con reasoning de Gemini
        print("\nTODOS LOS CORREOS POR CATEGORIA:")
        print("-" * 40)

        categories = ['urgent', 'high', 'medium', 'low']
        for category in categories:
            emails = Email.query.filter(Email.urgency_category == category).all()
            print(f"\n{category.upper()} ({len(emails)} correos):")

            for email in emails[:5]:  # Mostrar solo los primeros 5
                has_reasoning = bool(email.ai_reasoning and email.ai_reasoning.strip())
                reasoning_source = "GEMINI" if has_reasoning else "FALLBACK"
                print(f"  - {email.subject[:50]}... [{reasoning_source}]")

            if len(emails) > 5:
                print(f"  ... y {len(emails) - 5} más")

        return suspicious_emails

if __name__ == "__main__":
    suspicious = check_today_deadlines()

    if suspicious:
        print(f"\n⚠️  ENCONTRADOS {len(suspicious)} correos sospechosos!")
        print("Estos correos podrían necesitar reclasificación manual")
    else:
        print("\n✅ No se encontraron correos sospechosos")
        print("La clasificación parece correcta")