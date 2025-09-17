#!/usr/bin/env python3
"""
Generar 5 correos de prueba para cada nivel de prioridad
"""

from app import create_app
from app.services.openai_service import OpenAIService

def generate_test_emails():
    """Generar y probar 5 correos de diferentes prioridades."""
    app = create_app()
    
    with app.app_context():
        service = OpenAIService()
        
        # 5 correos de prueba diferentes
        test_emails = [
            {
                'name': 'URGENTE - Emergencia médica',
                'subject': 'EMERGENCIA: Estudiante desmayado en laboratorio de computación',
                'sender_name': 'Prof. Ana Martínez',
                'sender_email': 'ana.martinez@uss.cl',
                'body_preview': 'Directora Silva, URGENTE. El estudiante Carlos Mendoza se desmayó en el laboratorio de computación durante la clase de Programación Avanzada. Está inconsciente y sangrando de la cabeza. Ya llamé a la ambulancia pero necesito su autorización inmediata para el traslado al hospital. Los estudiantes están asustados y no sé qué hacer. Por favor responda URGENTEMENTE.',
                'expected': 'urgent'
            },
            {
                'name': 'ALTA - Problema académico grave',
                'subject': 'URGENTE: Problema grave con sistema de calificaciones',
                'sender_name': 'Prof. Roberto Silva',
                'sender_email': 'roberto.silva@uss.cl',
                'body_preview': 'Directora, necesito reunirme con usted URGENTEMENTE hoy antes de las 3:00 PM. Hay un problema crítico con el sistema de calificaciones - todas las notas del semestre se han perdido y los estudiantes no pueden ver sus calificaciones. Esto afecta a 150 estudiantes de tercer año. Necesitamos resolver esto HOY antes de que se convierta en un escándalo mayor.',
                'expected': 'high'
            },
            {
                'name': 'MEDIA - Solicitud con plazo definido',
                'subject': 'Solicitud de cambio de sección - Materia Base de Datos',
                'sender_name': 'María González',
                'sender_email': 'maria.gonzalez@uss.cl',
                'body_preview': 'Estimada Directora Silva, le escribo para solicitar un cambio de sección en la materia Base de Datos del tercer año. Actualmente estoy en la sección A (lunes y miércoles 8:00-10:00 AM) pero necesito cambiarme a la sección B (martes y jueves 2:00-4:00 PM) por un conflicto de horario con mi trabajo. El plazo para cambios de sección vence el próximo viernes 25 de septiembre. ¿Podríamos coordinar una reunión esta semana para revisar mi solicitud?',
                'expected': 'medium'
            },
            {
                'name': 'BAJA - Consulta general',
                'subject': 'Consulta sobre horarios del próximo semestre',
                'sender_name': 'Pedro Ramírez',
                'sender_email': 'pedro.ramirez@uss.cl',
                'body_preview': 'Hola Directora Silva, espero se encuentre bien. Soy estudiante de segundo año de ICIF y tengo una consulta sobre los horarios del próximo semestre. ¿Podría confirmarme si las clases de Estructura de Datos se mantendrán en el mismo horario de 10:00 AM a 12:00 PM los martes y jueves? También me gustaría saber si habrá cambios en los profesores. Gracias por su tiempo.',
                'expected': 'low'
            },
            {
                'name': 'BAJA - Información general',
                'subject': 'Invitación a evento de networking tecnológico',
                'sender_name': 'Comité de Egresados ICIF',
                'sender_email': 'egresados.icif@uss.cl',
                'body_preview': 'Estimada Directora Silva, el Comité de Egresados de ICIF tiene el agrado de invitarle al evento de networking tecnológico "Innovación y Emprendimiento" que se realizará el próximo sábado 28 de septiembre de 9:00 AM a 5:00 PM en el auditorio principal. El evento contará con la participación de destacados egresados y empresarios del sector tecnológico. Confirmar asistencia antes del 20 de septiembre.',
                'expected': 'low'
            }
        ]
        
        print("=== PROBANDO 5 CORREOS DE DIFERENTES PRIORIDADES ===\n")
        
        results = []
        
        for i, email_data in enumerate(test_emails, 1):
            print(f"--- CORREO {i}: {email_data['name']} ---")
            print(f"Asunto: {email_data['subject']}")
            print(f"Remitente: {email_data['sender_name']} <{email_data['sender_email']}>")
            print()
            
            # Clasificar
            result = service.classify_email(email_data)
            
            print(f"✅ RESULTADO:")
            print(f"Urgencia: {result['urgency_category']}")
            print(f"Confianza: {result['confidence_score']}")
            print(f"Razonamiento: {result['reasoning'][:100]}...")
            
            # Verificar si es correcto
            is_correct = result['urgency_category'] == email_data['expected']
            status = "✅ CORRECTO" if is_correct else "❌ INCORRECTO"
            print(f"Esperado: {email_data['expected']} | {status}")
            
            results.append({
                'name': email_data['name'],
                'expected': email_data['expected'],
                'actual': result['urgency_category'],
                'correct': is_correct,
                'confidence': result['confidence_score']
            })
            
            print("-" * 80)
            print()
        
        # Resumen final
        print("=== RESUMEN FINAL ===")
        correct_count = sum(1 for r in results if r['correct'])
        total_count = len(results)
        
        print(f"Correos clasificados correctamente: {correct_count}/{total_count}")
        print(f"Precisión: {(correct_count/total_count)*100:.1f}%")
        print()
        
        for result in results:
            status = "✅" if result['correct'] else "❌"
            print(f"{status} {result['name']}: {result['expected']} → {result['actual']} (confianza: {result['confidence']})")

if __name__ == "__main__":
    generate_test_emails()
