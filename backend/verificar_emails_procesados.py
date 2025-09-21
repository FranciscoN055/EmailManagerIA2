#!/usr/bin/env python3
"""
Script para verificar emails procesados y su persistencia
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Agregar el directorio app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def verificar_emails_procesados():
    """Verificar emails procesados y su persistencia"""
    
    print("📧 VERIFICACIÓN DE EMAILS PROCESADOS")
    print("=" * 50)
    
    try:
        # Importar modelos y configurar Flask
        from app import create_app, db
        from app.models.email import Email
        from app.models.email_account import EmailAccount
        from app.models.user import User
        
        app = create_app()
        
        with app.app_context():
            # Obtener estadísticas de emails procesados
            total_emails = Email.query.count()
            processed_emails = Email.query.filter_by(processing_status='processed').count()
            completed_emails = Email.query.filter_by(processing_status='completed').count()
            pending_emails = Email.query.filter_by(processing_status='pending').count()
            
            print(f"📊 ESTADÍSTICAS DE EMAILS:")
            print(f"   Total de emails: {total_emails}")
            print(f"   Procesados: {processed_emails}")
            print(f"   Completados: {completed_emails}")
            print(f"   Pendientes: {pending_emails}")
            
            # Verificar emails con urgency_category = 'processed'
            processed_by_urgency = Email.query.filter_by(urgency_category='processed').count()
            print(f"   Con urgencia 'processed': {processed_by_urgency}")
            
            # Verificar emails marcados como leídos
            read_emails = Email.query.filter_by(is_read=True).count()
            print(f"   Marcados como leídos: {read_emails}")
            
            # Mostrar emails procesados recientes
            print(f"\n📅 EMAILS PROCESADOS RECIENTES:")
            recent_processed = Email.query.filter(
                Email.processing_status == 'processed'
            ).order_by(Email.updated_at.desc()).limit(10).all()
            
            for email in recent_processed:
                print(f"   ✅ {email.subject[:50]}... - {email.urgency_category} - {email.updated_at.strftime('%Y-%m-%d %H:%M')}")
            
            # Verificar si hay diferencias entre processing_status y urgency_category
            print(f"\n🔍 VERIFICACIÓN DE CONSISTENCIA:")
            
            # Emails con processing_status='processed' pero urgency_category diferente
            inconsistent_processed = Email.query.filter(
                Email.processing_status == 'processed',
                Email.urgency_category != 'processed'
            ).count()
            
            print(f"   Emails con processing_status='processed' pero urgency_category diferente: {inconsistent_processed}")
            
            # Emails con urgency_category='processed' pero processing_status diferente
            inconsistent_urgency = Email.query.filter(
                Email.urgency_category == 'processed',
                Email.processing_status != 'processed'
            ).count()
            
            print(f"   Emails con urgency_category='processed' pero processing_status diferente: {inconsistent_urgency}")
            
            # Verificar persistencia - emails que se mantienen como procesados
            print(f"\n💾 VERIFICACIÓN DE PERSISTENCIA:")
            
            # Emails que han sido procesados y se mantienen así
            persistent_processed = Email.query.filter(
                Email.processing_status == 'processed',
                Email.urgency_category == 'processed'
            ).count()
            
            print(f"   Emails consistentemente procesados: {persistent_processed}")
            
            # Mostrar algunos ejemplos de emails procesados
            if persistent_processed > 0:
                print(f"\n📋 EJEMPLOS DE EMAILS PROCESADOS:")
                examples = Email.query.filter(
                    Email.processing_status == 'processed',
                    Email.urgency_category == 'processed'
                ).order_by(Email.updated_at.desc()).limit(5).all()
                
                for email in examples:
                    print(f"   • {email.subject[:40]}...")
                    print(f"     - ID: {email.id}")
                    print(f"     - Procesado: {email.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"     - Leído: {email.is_read}")
                    print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def mostrar_diferencias_entre_usuarios():
    """Mostrar posibles diferencias entre usuarios"""
    
    print("\n" + "="*60)
    print("🔍 POSIBLES DIFERENCIAS ENTRE USUARIOS")
    print("="*60)
    
    print("\n1️⃣ DIFERENCIAS EN LA BASE DE DATOS:")
    print("   • Tu sistema: Emails se marcan como 'processed' y se mantienen")
    print("   • Su sistema: Emails NO se marcan como 'processed' o se revierten")
    print("   • Posible causa: Diferentes configuraciones de base de datos")
    
    print("\n2️⃣ DIFERENCIAS EN EL CÓDIGO:")
    print("   • Tu sistema: Código actualizado con persistencia")
    print("   • Su sistema: Código anterior sin persistencia")
    print("   • Posible causa: Diferentes versiones del código")
    
    print("\n3️⃣ DIFERENCIAS EN LA CONFIGURACIÓN:")
    print("   • Tu sistema: Configuración correcta de la base de datos")
    print("   • Su sistema: Configuración incorrecta o base de datos diferente")
    print("   • Posible causa: Diferentes archivos .env o configuraciones")
    
    print("\n4️⃣ DIFERENCIAS EN EL COMPORTAMIENTO:")
    print("   • Tu sistema: Respuestas se envían y se marcan como procesadas")
    print("   • Su sistema: Respuestas fallan o no se marcan correctamente")
    print("   • Posible causa: Errores en el envío de respuestas")

def mostrar_soluciones():
    """Mostrar soluciones para el problema"""
    
    print("\n" + "="*60)
    print("🛠️  SOLUCIONES PARA EL PROBLEMA")
    print("="*60)
    
    print("\n1️⃣ VERIFICAR CONFIGURACIÓN DE BASE DE DATOS:")
    print("   • Comparar archivos .env")
    print("   • Verificar conexión a la base de datos")
    print("   • Revisar permisos de escritura")
    
    print("\n2️⃣ VERIFICAR CÓDIGO:")
    print("   • Comparar versiones del código")
    print("   • Verificar que tenga la última versión")
    print("   • Revisar logs de errores")
    
    print("\n3️⃣ VERIFICAR FUNCIONALIDAD DE RESPUESTAS:")
    print("   • Probar envío de respuestas")
    print("   • Verificar que se marquen como procesadas")
    print("   • Revisar logs de Microsoft Graph")
    
    print("\n4️⃣ SINCRONIZAR CONFIGURACIONES:")
    print("   • Asegurar que ambos tengan el mismo código")
    print("   • Verificar configuraciones idénticas")
    print("   • Revisar variables de entorno")

if __name__ == "__main__":
    verificar_emails_procesados()
    mostrar_diferencias_entre_usuarios()
    mostrar_soluciones()
