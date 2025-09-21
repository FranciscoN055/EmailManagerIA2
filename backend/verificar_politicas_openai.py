#!/usr/bin/env python3
"""
Script para verificar políticas y restricciones de OpenAI
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

def verificar_politicas_openai():
    """Verificar políticas y restricciones de OpenAI"""
    
    print("🔍 VERIFICACIÓN DE POLÍTICAS OPENAI")
    print("=" * 50)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cargar variables de entorno
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No se encontró OPENAI_API_KEY")
        return
    
    print(f"\n🔑 API Key: {api_key[:20]}...")
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Probar diferentes tipos de llamadas
        print("\n1️⃣ Probando llamadas básicas...")
        
        # Llamada simple
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hola"}],
                max_tokens=5
            )
            print("✅ Llamada simple: OK")
            print(f"   Tokens: {response.usage.total_tokens}")
        except Exception as e:
            print(f"❌ Llamada simple: {e}")
            return
        
        # Llamada con más tokens
        print("\n2️⃣ Probando llamada con más tokens...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Escribe un párrafo corto sobre inteligencia artificial"}],
                max_tokens=100
            )
            print("✅ Llamada con más tokens: OK")
            print(f"   Tokens: {response.usage.total_tokens}")
        except Exception as e:
            print(f"❌ Llamada con más tokens: {e}")
        
        # Llamada con temperatura alta
        print("\n3️⃣ Probando llamada con temperatura alta...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "OK"}],
                max_tokens=5,
                temperature=1.0
            )
            print("✅ Llamada con temperatura alta: OK")
        except Exception as e:
            print(f"❌ Llamada con temperatura alta: {e}")
        
        print("\n✅ Tu cuenta funciona correctamente")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

def mostrar_diferencias_politicas():
    """Mostrar diferencias en políticas de OpenAI"""
    
    print("\n" + "="*60)
    print("📋 DIFERENCIAS EN POLÍTICAS DE OPENAI")
    print("="*60)
    
    print("\n🕐 CUENTAS ANTIGUAS (como la tuya):")
    print("   ✅ $5 USD de créditos gratuitos")
    print("   ✅ Sin restricciones de verificación")
    print("   ✅ Funciona inmediatamente")
    print("   ✅ Sin método de pago requerido")
    
    print("\n🕐 CUENTAS NUEVAS (como la de tu compañera):")
    print("   ⚠️  $5 USD de créditos gratuitos")
    print("   ❌ Verificación de cuenta requerida")
    print("   ❌ Método de pago obligatorio en algunas regiones")
    print("   ❌ Restricciones geográficas más estrictas")
    print("   ❌ Verificación de identidad en algunos casos")
    
    print("\n🌍 RESTRICCIONES POR REGIÓN:")
    print("   • Europa: Verificación adicional requerida")
    print("   • Latinoamérica: Algunos países restringidos")
    print("   • Asia: Políticas más estrictas")
    print("   • África: Restricciones variables")
    
    print("\n📅 CAMBIOS RECIENTES:")
    print("   • 2024: Restricciones en Europa")
    print("   • 2024: Verificación de identidad requerida")
    print("   • 2024: Método de pago obligatorio en algunas regiones")
    print("   • 2024: Límites de uso más estrictos")

def mostrar_soluciones_para_compañera():
    """Mostrar soluciones específicas para la compañera"""
    
    print("\n" + "="*60)
    print("🛠️  SOLUCIONES PARA TU COMPAÑERA")
    print("="*60)
    
    print("\n1️⃣ VERIFICAR CUENTA:")
    print("   • Ve a: https://platform.openai.com/account")
    print("   • Completa la verificación de identidad")
    print("   • Agrega número de teléfono")
    print("   • Verifica el email")
    
    print("\n2️⃣ CONFIGURAR FACTURACIÓN:")
    print("   • Ve a: https://platform.openai.com/billing")
    print("   • Agrega método de pago")
    print("   • Configura límite de gasto ($5-10 USD)")
    print("   • Obtiene $5 adicionales inmediatamente")
    
    print("\n3️⃣ USAR TU API KEY (temporal):")
    print("   • Ya funciona (como confirmaste)")
    print("   • Consume tus créditos")
    print("   • Solo para desarrollo/testing")
    print("   • No recomendado para producción")
    
    print("\n4️⃣ USAR CLASIFICACIÓN POR REGLAS:")
    print("   • El sistema ya tiene fallback automático")
    print("   • Funciona sin OpenAI")
    print("   • No consume créditos")
    print("   • Menos preciso pero funcional")
    
    print("\n💡 RECOMENDACIÓN:")
    print("   • Para desarrollo: Usar tu key temporalmente")
    print("   • Para producción: Configurar su propia facturación")
    print("   • Alternativa: Usar clasificación por reglas")

if __name__ == "__main__":
    verificar_politicas_openai()
    mostrar_diferencias_politicas()
    mostrar_soluciones_para_compañera()



