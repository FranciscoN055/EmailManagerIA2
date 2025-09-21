#!/usr/bin/env python3
"""
Script para verificar el estado de la base de datos
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Agregar el directorio app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def verificar_base_datos():
    """Verificar el estado de la base de datos"""
    
    print("🗄️  VERIFICACIÓN DE BASE DE DATOS")
    print("=" * 50)
    
    try:
        # Importar modelos y configurar Flask
        from app import create_app, db
        from app.models.email import Email
        from app.models.email_account import EmailAccount
        from app.models.user import User
        
        app = create_app()
        
        with app.app_context():
            # 1. Verificar conexión a la base de datos
            print("1️⃣ Verificando conexión a la base de datos...")
            try:
                # Intentar una consulta simple
                result = db.session.execute(db.text("SELECT 1")).fetchone()
                print("✅ Conexión a la base de datos: OK")
            except Exception as e:
                print(f"❌ Error de conexión: {e}")
                return
            
            # 2. Verificar configuración de la base de datos
            print("\n2️⃣ Verificando configuración de la base de datos...")
            from app.config import Config
            config = Config()
            
            print(f"   Tipo de base de datos: {config.SQLALCHEMY_DATABASE_URI}")
            
            # 3. Verificar tablas existentes
            print("\n3️⃣ Verificando tablas existentes...")
            try:
                # Verificar si las tablas existen
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                
                required_tables = ['user', 'email_account', 'email']
                print(f"   Tablas encontradas: {tables}")
                
                for table in required_tables:
                    if table in tables:
                        print(f"   ✅ Tabla '{table}': Existe")
                    else:
                        print(f"   ❌ Tabla '{table}': NO existe")
                        
            except Exception as e:
                print(f"❌ Error al verificar tablas: {e}")
            
            # 4. Verificar datos en las tablas
            print("\n4️⃣ Verificando datos en las tablas...")
            try:
                user_count = User.query.count()
                email_account_count = EmailAccount.query.count()
                email_count = Email.query.count()
                
                print(f"   Usuarios: {user_count}")
                print(f"   Cuentas de email: {email_account_count}")
                print(f"   Emails: {email_count}")
                
            except Exception as e:
                print(f"❌ Error al verificar datos: {e}")
            
            # 5. Verificar permisos de escritura
            print("\n5️⃣ Verificando permisos de escritura...")
            try:
                # Intentar crear un registro de prueba
                test_email = Email(
                    subject="Test Email",
                    sender_email="test@example.com",
                    sender_name="Test Sender",
                    body_preview="Test body",
                    received_at=datetime.now()
                )
                
                db.session.add(test_email)
                db.session.commit()
                
                # Eliminar el registro de prueba
                db.session.delete(test_email)
                db.session.commit()
                
                print("✅ Permisos de escritura: OK")
                
            except Exception as e:
                print(f"❌ Error de permisos de escritura: {e}")
            
            # 6. Verificar estado de la base de datos
            print("\n6️⃣ Verificando estado de la base de datos...")
            try:
                # Verificar si hay emails procesados
                processed_emails = Email.query.filter_by(processing_status='processed').count()
                print(f"   Emails procesados: {processed_emails}")
                
                # Verificar si hay emails con urgency_category='processed'
                urgency_processed = Email.query.filter_by(urgency_category='processed').count()
                print(f"   Emails con urgencia 'processed': {urgency_processed}")
                
                # Verificar si hay emails leídos
                read_emails = Email.query.filter_by(is_read=True).count()
                print(f"   Emails leídos: {read_emails}")
                
            except Exception as e:
                print(f"❌ Error al verificar estado: {e}")
            
            # 7. Verificar logs de la base de datos
            print("\n7️⃣ Verificando logs de la base de datos...")
            try:
                # Verificar si hay errores en los logs
                error_emails = Email.query.filter_by(processing_status='error').count()
                print(f"   Emails con error: {error_emails}")
                
                if error_emails > 0:
                    print("   ⚠️  Hay emails con errores de procesamiento")
                else:
                    print("   ✅ No hay emails con errores")
                    
            except Exception as e:
                print(f"❌ Error al verificar logs: {e}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

def mostrar_soluciones_base_datos():
    """Mostrar soluciones para problemas de base de datos"""
    
    print("\n" + "="*60)
    print("🛠️  SOLUCIONES PARA PROBLEMAS DE BASE DE DATOS")
    print("="*60)
    
    print("\n1️⃣ SI LA BASE DE DATOS NO ESTÁ INICIADA:")
    print("   • Verificar que el servicio de base de datos esté corriendo")
    print("   • Iniciar la base de datos si es necesario")
    print("   • Verificar la configuración de conexión")
    
    print("\n2️⃣ SI HAY PROBLEMAS DE CONEXIÓN:")
    print("   • Verificar el archivo .env")
    print("   • Revisar la URL de conexión")
    print("   • Verificar credenciales")
    
    print("\n3️⃣ SI FALTAN TABLAS:")
    print("   • Ejecutar migraciones:")
    print("     flask db upgrade")
    print("   • O crear las tablas:")
    print("     flask db init")
    print("     flask db migrate")
    print("     flask db upgrade")
    
    print("\n4️⃣ SI HAY PROBLEMAS DE PERMISOS:")
    print("   • Verificar permisos de escritura")
    print("   • Revisar configuración de usuario")
    print("   • Verificar espacio en disco")
    
    print("\n5️⃣ SI HAY PROBLEMAS DE PERSISTENCIA:")
    print("   • Verificar que los cambios se guarden")
    print("   • Revisar transacciones de la base de datos")
    print("   • Verificar logs de errores")

def verificar_configuracion_env():
    """Verificar configuración del archivo .env"""
    
    print("\n" + "="*60)
    print("🔧 VERIFICACIÓN DE CONFIGURACIÓN .ENV")
    print("="*60)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Verificar variables importantes
    database_url = os.getenv('DATABASE_URL')
    secret_key = os.getenv('SECRET_KEY')
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    
    print(f"📊 CONFIGURACIÓN ACTUAL:")
    print(f"   DATABASE_URL: {database_url[:50] + '...' if database_url else 'NO CONFIGURADA'}")
    print(f"   SECRET_KEY: {'CONFIGURADA' if secret_key else 'NO CONFIGURADA'}")
    print(f"   JWT_SECRET_KEY: {'CONFIGURADA' if jwt_secret else 'NO CONFIGURADA'}")
    
    if not database_url:
        print("\n❌ PROBLEMA: DATABASE_URL no está configurada")
        print("💡 SOLUCIÓN: Agregar DATABASE_URL al archivo .env")
        print("   Ejemplo: DATABASE_URL=sqlite:///email_manager.db")
    
    if not secret_key:
        print("\n❌ PROBLEMA: SECRET_KEY no está configurada")
        print("💡 SOLUCIÓN: Agregar SECRET_KEY al archivo .env")
        print("   Ejemplo: SECRET_KEY=tu-secret-key-aqui")
    
    if not jwt_secret:
        print("\n❌ PROBLEMA: JWT_SECRET_KEY no está configurada")
        print("💡 SOLUCIÓN: Agregar JWT_SECRET_KEY al archivo .env")
        print("   Ejemplo: JWT_SECRET_KEY=tu-jwt-secret-aqui")

if __name__ == "__main__":
    verificar_base_datos()
    mostrar_soluciones_base_datos()
    verificar_configuracion_env()
