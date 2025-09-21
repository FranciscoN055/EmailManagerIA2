#!/usr/bin/env python3
"""
Script de diagnóstico para verificar configuración de OpenAI
"""

import os
import sys
from dotenv import load_dotenv

def diagnosticar_openai():
    """Diagnosticar configuración de OpenAI"""
    
    print("🔍 DIAGNÓSTICO DE OPENAI - Email Manager IA")
    print("=" * 60)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # 1. Verificar archivo .env
    print("\n1️⃣ Verificando archivo .env...")
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print("✅ Archivo .env encontrado")
    else:
        print("❌ Archivo .env NO encontrado")
        print("💡 Solución: Crear archivo .env con tu API key")
        return False
    
    # 2. Verificar API key
    print("\n2️⃣ Verificando OPENAI_API_KEY...")
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY no encontrada")
        print("💡 Solución: Agregar OPENAI_API_KEY=tu-key-aqui al archivo .env")
        return False
    
    if api_key == 'your-openai-api-key-here':
        print("❌ OPENAI_API_KEY tiene valor por defecto")
        print("💡 Solución: Reemplazar con tu API key real")
        return False
    
    print(f"✅ OPENAI_API_KEY encontrada: {api_key[:20]}...")
    
    # 3. Verificar otras configuraciones
    print("\n3️⃣ Verificando otras configuraciones...")
    
    model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    max_tokens = os.getenv('OPENAI_MAX_TOKENS', '1000')
    temperature = os.getenv('OPENAI_TEMPERATURE', '0.3')
    
    print(f"   Modelo: {model}")
    print(f"   Max tokens: {max_tokens}")
    print(f"   Temperature: {temperature}")
    
    # 4. Probar conexión
    print("\n4️⃣ Probando conexión con OpenAI...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Llamada simple
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Responde solo 'OK'"}
            ],
            max_tokens=5
        )
        
        content = response.choices[0].message.content.strip()
        print(f"✅ Conexión exitosa: '{content}'")
        
        # Mostrar uso de tokens
        usage = response.usage
        print(f"   Tokens consumidos: {usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def mostrar_solucion():
    """Mostrar solución paso a paso"""
    
    print("\n" + "="*60)
    print("🛠️  SOLUCIÓN PASO A PASO")
    print("="*60)
    
    print("\n1️⃣ Crear cuenta en OpenAI:")
    print("   • Ve a: https://platform.openai.com")
    print("   • Regístrate (gratis)")
    print("   • Verifica tu email")
    
    print("\n2️⃣ Obtener API Key:")
    print("   • Ve a: https://platform.openai.com/api-keys")
    print("   • Click 'Create new secret key'")
    print("   • Copia la key (empieza con sk-proj-)")
    
    print("\n3️⃣ Crear archivo .env:")
    print("   • En la carpeta 'backend' crea archivo .env")
    print("   • Agrega esta línea:")
    print("     OPENAI_API_KEY=sk-proj-tu-key-aqui")
    
    print("\n4️⃣ Verificar configuración:")
    print("   • Ejecuta: python diagnostico_openai.py")
    print("   • Debe mostrar '✅ Conexión exitosa'")
    
    print("\n💰 Sobre los créditos:")
    print("   • OpenAI da $5 USD gratis al registrarse")
    print("   • Es suficiente para cientos de clasificaciones")
    print("   • No necesitas meter dinero inicialmente")

def main():
    """Función principal"""
    
    # Ejecutar diagnóstico
    funciona = diagnosticar_openai()
    
    if funciona:
        print("\n🎉 ¡TODO FUNCIONA CORRECTAMENTE!")
        print("✅ Tu configuración de OpenAI está bien")
        print("✅ El sistema debería clasificar emails con IA")
    else:
        print("\n⚠️  HAY PROBLEMAS DE CONFIGURACIÓN")
        mostrar_solucion()
    
    print("\n" + "="*60)
    print("💡 Si sigues teniendo problemas, contacta al equipo de desarrollo")

if __name__ == "__main__":
    main()
