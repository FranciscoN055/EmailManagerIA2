#!/usr/bin/env python3
"""
Verificar resultados de clasificación
"""

from app import create_app
from app.models.email import Email

def check_results():
    """Verificar resultados de clasificación."""
    app = create_app()
    
    with app.app_context():
        emails = Email.query.all()
        
        print(f"=== ESTADÍSTICAS DE CLASIFICACIÓN ===")
        print(f"Total emails: {len(emails)}")
        print(f"Classified: {sum(1 for e in emails if e.is_classified)}")
        print(f"Pending: {sum(1 for e in emails if not e.is_classified)}")
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

if __name__ == "__main__":
    check_results()
