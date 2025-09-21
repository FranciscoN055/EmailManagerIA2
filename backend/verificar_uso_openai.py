#!/usr/bin/env python3
"""
Script para verificar el uso actual de OpenAI
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, timedelta

def verificar_uso_openai():
    """Verificar uso actual de OpenAI"""
    
    print("📊 VERIFICACIÓN DE USO OPENAI")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No se encontró OPENAI_API_KEY")
        return
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Obtener fecha de hace 30 días
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print(f"📅 Período: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")
        
        # Intentar obtener uso (esto puede fallar si no hay permisos)
        try:
            usage = client.usage.retrieve(
                start_date=start_date,
                end_date=end_date
            )
            
            print(f"\n💰 Uso en los últimos 30 días:")
            print(f"   Total de tokens: {usage.total_tokens:,}")
            print(f"   Costo total: ${usage.total_cost:.4f}")
            
        except Exception as e:
            print(f"⚠️  No se pudo obtener el uso detallado: {e}")
            print("💡 Ve a https://platform.openai.com/usage para ver el uso")
        
        # Probar una llamada simple para verificar estado
        print(f"\n🧪 Probando llamada simple...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hola"}],
                max_tokens=5
            )
            
            print("✅ API funcionando correctamente")
            print(f"   Tokens usados: {response.usage.total_tokens}")
            
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                print("❌ CUOTA EXCEDIDA - Se agotaron los créditos")
                print("💡 Soluciones:")
                print("   1. Agregar método de pago en https://platform.openai.com/billing")
                print("   2. Usar clasificación por reglas (fallback automático)")
                print("   3. Esperar renovación de créditos (si aplica)")
            else:
                print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Error general: {e}")

def mostrar_alternativas():
    """Mostrar alternativas cuando no hay créditos"""
    
    print("\n" + "="*50)
    print("🔄 ALTERNATIVAS SIN CRÉDITOS OPENAI")
    print("="*50)
    
    print("\n1️⃣ Clasificación por reglas (automática):")
    print("   • El sistema detecta automáticamente si no hay OpenAI")
    print("   • Usa palabras clave para clasificar")
    print("   • Funciona sin créditos")
    print("   • Menos preciso pero funcional")
    
    print("\n2️⃣ Configurar método de pago:")
    print("   • Ve a: https://platform.openai.com/billing")
    print("   • Agrega tarjeta de crédito")
    print("   • Configura límite de gasto ($5-10 USD)")
    print("   • Obtienes $5 adicionales")
    
    print("\n3️⃣ Usar API key compartida (temporal):")
    print("   • Solo para desarrollo/testing")
    print("   • Consumirá créditos del propietario")
    print("   • No recomendado para producción")

if __name__ == "__main__":
    verificar_uso_openai()
    mostrar_alternativas()
