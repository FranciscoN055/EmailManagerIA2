#!/usr/bin/env python3
"""
Script para verificar qué base de datos está usando actualmente
"""

import os
import sys
from dotenv import load_dotenv

# Agregar el directorio app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def verificar_base_datos_actual():
    """Verificar qué base de datos está usando actualmente"""
    
    print("🔍 VERIFICACIÓN DE BASE DE DATOS ACTUAL")
    print("=" * 50)
    
    try:
        # Importar y configurar Flask
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            # 1. Verificar configuración
            print("1️⃣ Configuración de base de datos:")
            database_uri = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"   URI: {database_uri}")
            
            if 'sqlite' in database_uri:
                print("   ✅ Usando SQLite")
                db_file = database_uri.replace('sqlite:///', '')
                print(f"   Archivo: {db_file}")
                
                # Verificar si el archivo existe
                if os.path.exists(db_file):
                    print("   ✅ Archivo de base de datos existe")
                    
                    # Verificar tablas
                    import sqlite3
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    print(f"   Tablas: {[table[0] for table in tables]}")
                    conn.close()
                else:
                    print("   ❌ Archivo de base de datos NO existe")
                    
            elif 'postgresql' in database_uri:
                print("   ✅ Usando PostgreSQL")
                print("   ⚠️  Requiere servidor PostgreSQL corriendo")
            else:
                print("   ❓ Tipo de base de datos desconocido")
            
            # 2. Verificar conexión
            print("\n2️⃣ Verificación de conexión:")
            try:
                from app import db
                result = db.session.execute(db.text("SELECT 1")).fetchone()
                print("   ✅ Conexión exitosa")
            except Exception as e:
                print(f"   ❌ Error de conexión: {e}")
            
            # 3. Verificar datos
            print("\n3️⃣ Verificación de datos:")
            try:
                from app.models.email import Email
                from app.models.user import User
                from app.models.email_account import EmailAccount
                
                user_count = User.query.count()
                email_count = Email.query.count()
                account_count = EmailAccount.query.count()
                
                print(f"   Usuarios: {user_count}")
                print(f"   Emails: {email_count}")
                print(f"   Cuentas: {account_count}")
                
            except Exception as e:
                print(f"   ❌ Error al verificar datos: {e}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

def mostrar_resumen():
    """Mostrar resumen de la configuración"""
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE CONFIGURACIÓN")
    print("="*60)
    
    # Cargar variables de entorno
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        print(f"🔧 DATABASE_URL configurada: {database_url}")
        if 'sqlite' in database_url:
            print("   → Usando SQLite (archivo local)")
        elif 'postgresql' in database_url:
            print("   → Usando PostgreSQL (servidor)")
        else:
            print("   → Tipo de base de datos desconocido")
    else:
        print("🔧 DATABASE_URL NO configurada")
        print("   → Usando valor por defecto: sqlite:///email_manager.db")
        print("   → Usando SQLite (archivo local)")

if __name__ == "__main__":
    verificar_base_datos_actual()
    mostrar_resumen()
