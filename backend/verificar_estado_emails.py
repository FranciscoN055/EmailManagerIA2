#!/usr/bin/env python3
"""
Script para verificar el estado de procesamiento de emails
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Agregar el directorio app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def verificar_estado_emails():
    """Verificar el estado de procesamiento de emails"""
    
    print("📧 VERIFICACIÓN DE ESTADO DE EMAILS")
    print("=" * 50)
    
    try:
        # Importar modelos y configurar Flask
        from app import create_app, db
        from app.models.email import Email
        from app.models.email_account import EmailAccount
        from app.models.user import User
        
        app = create_app()
        
        with app.app_context():
            # Obtener estadísticas de emails
            total_emails = Email.query.count()
            pending_emails = Email.query.filter_by(processing_status='pending').count()
            completed_emails = Email.query.filter_by(processing_status='completed').count()
            classified_emails = Email.query.filter_by(processing_status='classified').count()
            error_emails = Email.query.filter_by(processing_status='error').count()
            
            print(f"📊 ESTADÍSTICAS DE EMAILS:")
            print(f"   Total de emails: {total_emails}")
            print(f"   Pendientes: {pending_emails}")
            print(f"   Completados: {completed_emails}")
            print(f"   Clasificados: {classified_emails}")
            print(f"   Con error: {error_emails}")
            
            # Verificar emails recientes
            print(f"\n📅 EMAILS RECIENTES (últimas 24 horas):")
            from datetime import timedelta
            recent_time = datetime.now() - timedelta(hours=24)
            
            recent_emails = Email.query.filter(
                Email.created_at >= recent_time
            ).order_by(Email.created_at.desc()).limit(10).all()
            
            for email in recent_emails:
                status_icon = "✅" if email.processing_status == 'completed' else "⏳" if email.processing_status == 'pending' else "❌"
                print(f"   {status_icon} {email.subject[:50]}... - {email.processing_status}")
            
            # Verificar configuración de OpenAI
            print(f"\n🤖 CONFIGURACIÓN DE OPENAI:")
            from app.services.openai_service import OpenAIService
            
            openai_service = OpenAIService()
            status = openai_service.get_status()
            
            print(f"   Estado: {status['status']}")
            print(f"   Mensaje: {status['message']}")
            print(f"   Modelo: {status['model']}")
            
            # Verificar si hay emails que necesitan clasificación
            unclassified_emails = Email.query.filter(
                Email.processing_status == 'pending',
                Email.is_classified == False
            ).count()
            
            print(f"\n🔄 EMAILS QUE NECESITAN CLASIFICACIÓN:")
            print(f"   Emails pendientes: {unclassified_emails}")
            
            if unclassified_emails > 0:
                print(f"\n💡 SOLUCIÓN:")
                print(f"   • Ejecutar clasificación manual")
                print(f"   • Verificar configuración de OpenAI")
                print(f"   • Revisar logs de errores")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def mostrar_soluciones():
    """Mostrar soluciones para el problema"""
    
    print("\n" + "="*60)
    print("🛠️  SOLUCIONES PARA EL PROBLEMA")
    print("="*60)
    
    print("\n1️⃣ VERIFICAR CONFIGURACIÓN DE OPENAI:")
    print("   • Ejecutar: python diagnostico_openai.py")
    print("   • Verificar que la API key funcione")
    print("   • Revisar logs de errores")
    
    print("\n2️⃣ CLASIFICAR EMAILS MANUALMENTE:")
    print("   • Usar el endpoint /api/emails/classify")
    print("   • Con parámetro classify_all_pending=true")
    print("   • Esto procesará todos los emails pendientes")
    
    print("\n3️⃣ VERIFICAR LOGS:")
    print("   • Revisar logs del servidor")
    print("   • Buscar errores de OpenAI")
    print("   • Verificar conexión a la base de datos")
    
    print("\n4️⃣ USAR CLASIFICACIÓN POR REGLAS:")
    print("   • El sistema tiene fallback automático")
    print("   • Funciona sin OpenAI")
    print("   • Menos preciso pero funcional")

if __name__ == "__main__":
    verificar_estado_emails()
    mostrar_soluciones()
