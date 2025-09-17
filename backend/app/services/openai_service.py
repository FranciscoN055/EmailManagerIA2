"""
OpenAI Service
Handles AI-powered email classification using OpenAI GPT models.
Specialized for academic context - Universidad San Sebastián ICIF.
"""

from openai import OpenAI
from flask import current_app
import logging
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service class for OpenAI API operations with academic email classification."""
    
    def __init__(self, config=None):
        self.config = config or current_app.config
        self.api_key = self.config.get('OPENAI_API_KEY')
        self.model = self.config.get('OPENAI_MODEL', 'gpt-4o-mini')
        self.max_tokens = int(self.config.get('OPENAI_MAX_TOKENS', 800))
        self.temperature = float(self.config.get('OPENAI_TEMPERATURE', 0.3))
        
        self.client = None
        if self.api_key and self.api_key != 'your-openai-api-key-here':
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        
        # Academic context patterns - REAL urgent situations
        self.urgent_keywords = [
            'emergencia', 'accidente', 'hospital', 'ambulancia', 'lesion',
            'lesionado', 'herido', 'caída', 'golpe', 'sangre', 'desmayo',
            'crisis', 'problema grave', 'suspensión', 'expulsión', 'ayuda',
            'socorro', 'grave', 'inmediato', 'hoy mismo', 'crítico'
        ]
        
        # Non-urgent keywords that might be confused with urgent
        self.non_urgent_indicators = [
            'qué día', 'que dia', 'cuando', 'cuándo', 'horario', 'hora',
            'información', 'consulta', 'pregunta', 'duda', 'ayuda con',
            'necesito saber', 'podrías decirme', 'me puedes ayudar',
            'solo quería', 'solo queria', 'nada urgente', 'no es urgente',
            'cuando puedas', 'cuando tengas tiempo', 'no hay prisa'
        ]
        
        self.high_priority_keywords = [
            'reunión', 'junta', 'consejo', 'deadline', 'plazo', 'entrega',
            'examen', 'evaluación', 'presentación', 'defensa', 'tesis',
            'calificación', 'nota', 'reprobado', 'aprobado', 'suspensión',
            'expulsión', 'disciplinario', 'problema', 'conflicto', 'queja'
        ]
        
        self.academic_roles = {
            'estudiante': ['estudiante', 'alumno', 'alumna', '@uss.cl'],
            'profesor': ['profesor', 'profesora', 'docente', 'académico'],
            'administracion': ['secretaria', 'coordinador', 'director', 'decanato']
        }
    
    def get_status(self):
        """Get service status."""
        return {
            'service': 'OpenAIService',
            'status': 'ready' if self.api_key else 'no_api_key',
            'model': self.model,
            'message': 'OpenAI service ready for academic email classification' if self.api_key else 'OpenAI API key not configured'
        }
    
    def _build_classification_prompt(self, email_data: Dict) -> str:
        """Build specialized prompt for academic email classification."""
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        base_prompt = f"""
Eres un asistente inteligente especializado en clasificar correos electrónicos para Maritza Silva, 
Directora de la carrera ICIF en Universidad San Sebastián, Chile.

CONTEXTO ACADÉMICO:
- Directora de carrera universitaria
- Gestiona estudiantes, profesores y personal administrativo
- Debe responder a emergencias estudiantiles rápidamente
- Fechas importantes: exámenes, entregas, reuniones académicas
- Fecha actual: {current_date}

NIVELES DE URGENCIA:
1. URGENTE (próxima 1 hora): Emergencias médicas, accidentes estudiantiles, crisis de seguridad, situaciones que requieren acción INMEDIATA
2. ALTA (próximas 3 horas): Problemas académicos graves, reuniones urgentes hoy, deadlines críticos, estudiantes en crisis
3. MEDIA (hoy o próximos días): Solicitudes académicas con plazo definido, cambios de horario, coordinación con profesores, tareas administrativas que requieren seguimiento pero NO son emergencias
4. BAJA (mañana o más): Información general, invitaciones futuras, documentación no urgente, consultas sin plazo específico

PALABRAS CLAVE CRÍTICAS para URGENTE:
- Emergencias: accidente, lesión, hospital, ambulancia, herido, sangre, desmayo, caída
- Crisis: ayuda, socorro, crítico, grave, urgente, emergencia
- Seguridad: peligro, amenaza, violencia, drogas, alcohol

EJEMPLOS DE CLASIFICACIÓN:
- URGENTE: "Estudiante herido en laboratorio, necesita ambulancia"
- ALTA: "Reunión urgente hoy a las 3pm para resolver problema académico"
- MEDIA: "Solicitud cambio de horario con plazo viernes 20 septiembre"
- BAJA: "Consulta general sobre horarios del próximo semestre"

CORREO A CLASIFICAR:
Remitente: {email_data.get('sender_name', '')} <{email_data.get('sender_email', '')}>
Asunto: {email_data.get('subject', '')}
Fecha recibido: {email_data.get('received_at', '')}
Contenido: {email_data.get('body_preview', '')[:500]}

INSTRUCCIONES:
1. Analiza el contexto académico del remitente (estudiante/profesor/administración)
2. Identifica palabras clave de urgencia y deadlines
3. Considera la proximidad temporal de eventos mencionados
4. Evalúa el impacto en las responsabilidades de la directora

Responde SOLO en formato JSON válido:
{{
    "urgency_category": "urgent|high|medium|low",
    "confidence_score": 0.85,
    "reasoning": "Explicación breve de la clasificación",
    "sender_type": "estudiante|profesor|administracion|externo",
    "email_type": "academico|administrativo|personal|emergencia",
    "requires_immediate_action": true/false,
    "suggested_deadline": "2024-01-15T14:00:00" // o null
}}
"""
        
        return base_prompt.strip()
    
    def classify_email(self, email_data: Dict) -> Dict:
        """Classify a single email using OpenAI GPT-4."""
        
        logger.info(f"Starting email classification for: {email_data.get('subject', 'No subject')[:50]}...")
        logger.info(f"OpenAI client status: {self.client is not None}")
        logger.info(f"API key configured: {bool(self.api_key)}")
        logger.info(f"Model: {self.model}")
        
        if not self.client:
            logger.warning("OpenAI client not configured - using fallback")
            return self._fallback_classification(email_data)
        
        try:
            prompt = self._build_classification_prompt(email_data)
            logger.info(f"Prompt length: {len(prompt)} characters")
            
            logger.info("Making OpenAI API call...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en clasificación de correos académicos. Responde siempre en JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            logger.info("OpenAI API call successful")
            
            content = response.choices[0].message.content.strip()
            logger.info(f"OpenAI response received: {content[:200]}...")
            
            # Clean response - remove markdown formatting if present
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            if content.endswith('```'):
                content = content[:-3]  # Remove ```
            content = content.strip()
            
            # Parse JSON response
            try:
                classification = json.loads(content)
                logger.info(f"JSON parsed successfully: {classification}")
                
                # Validate required fields
                required_fields = ['urgency_category', 'confidence_score', 'reasoning']
                for field in required_fields:
                    if field not in classification:
                        raise ValueError(f"Missing required field: {field}")
                
                # Normalize urgency category
                urgency = classification['urgency_category'].lower()
                if urgency not in ['urgent', 'high', 'medium', 'low']:
                    urgency = 'medium'
                classification['urgency_category'] = urgency
                
                # Ensure confidence score is float between 0-1
                confidence = float(classification['confidence_score'])
                classification['confidence_score'] = max(0.0, min(1.0, confidence))
                
                logger.info(f"✅ Email classified as {urgency} with confidence {confidence}")
                return classification
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.error(f"❌ Error parsing OpenAI response: {e}")
                logger.error(f"Raw response: {content}")
                logger.warning("Falling back to rule-based classification")
                return self._fallback_classification(email_data)
        
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {str(e)}")
            logger.warning("Falling back to rule-based classification")
            return self._fallback_classification(email_data)
    
    def _fallback_classification(self, email_data: Dict) -> Dict:
        """Fallback classification when OpenAI is unavailable."""
        
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body_preview', '').lower()
        sender_email = email_data.get('sender_email', '').lower()
        text_content = f"{subject} {body}"
        
        # Rule-based classification - start with different defaults to avoid medium bias
        urgency = 'low'  # Start with low as default
        confidence = 0.6
        reasoning = "Clasificación basada en reglas (OpenAI no disponible)"
        
        # Check for non-urgent indicators first (to avoid false positives)
        has_non_urgent_indicators = any(keyword in text_content for keyword in self.non_urgent_indicators)
        has_urgent_keywords = any(keyword in text_content for keyword in self.urgent_keywords)
        
        # If it has non-urgent indicators, it's likely not urgent even if it says "urgente"
        if has_non_urgent_indicators and not has_urgent_keywords:
            urgency = 'low'
            confidence = 0.8
            reasoning = "Contenido indica consulta no urgente (a pesar de palabras como 'urgente')"
        
        # Check for REAL urgent keywords (only if no non-urgent indicators)
        elif has_urgent_keywords and not has_non_urgent_indicators:
            urgency = 'urgent'
            confidence = 0.9
            reasoning = "Detectadas palabras clave de urgencia crítica real"
        
        # Check for high priority keywords
        elif any(keyword in text_content for keyword in self.high_priority_keywords):
            urgency = 'high'
            confidence = 0.8
            reasoning = "Detectadas palabras clave de alta prioridad académica"
        
        # Check for medium priority indicators
        elif any(keyword in text_content for keyword in ['consulta', 'pregunta', 'ayuda', 'información', 'horario', 'clase', 'materia', 'asignatura']):
            urgency = 'medium'
            confidence = 0.7
            reasoning = "Consulta académica que requiere respuesta"
        
        # Student emails from USS get medium priority only if they contain academic content
        elif '@uss.cl' in sender_email:
            if any(keyword in text_content for keyword in ['consulta', 'pregunta', 'ayuda', 'información', 'horario', 'clase', 'materia', 'asignatura', 'profesor', 'docente']):
                urgency = 'medium'
                confidence = 0.7
                reasoning = "Correo de estudiante USS con contenido académico"
            else:
                urgency = 'low'
                confidence = 0.6
                reasoning = "Correo de estudiante USS - contenido general"
        
        # External emails are generally low priority unless urgent keywords
        else:
            urgency = 'low'
            confidence = 0.5
            reasoning = "Correo externo - prioridad baja"
        
        # Determine sender type
        sender_type = 'externo'
        if '@uss.cl' in sender_email:
            sender_type = 'estudiante'
        elif any(keyword in text_content for keyword in self.academic_roles['profesor']):
            sender_type = 'profesor'
        elif any(keyword in text_content for keyword in self.academic_roles['administracion']):
            sender_type = 'administracion'
        
        return {
            'urgency_category': urgency,
            'confidence_score': confidence,
            'reasoning': reasoning,
            'sender_type': sender_type,
            'email_type': 'academico',
            'requires_immediate_action': urgency in ['urgent', 'high'],
            'suggested_deadline': None
        }
    
    def classify_batch(self, emails_data: List[Dict], batch_size: int = 5) -> List[Dict]:
        """Classify multiple emails in batches to avoid rate limits."""
        
        results = []
        
        for i in range(0, len(emails_data), batch_size):
            batch = emails_data[i:i + batch_size]
            
            logger.info(f"Processing batch {i//batch_size + 1}, emails {i+1}-{min(i+batch_size, len(emails_data))}")
            
            batch_results = []
            for email_data in batch:
                try:
                    classification = self.classify_email(email_data)
                    batch_results.append(classification)
                    
                    # Small delay to avoid rate limiting
                    import time
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error classifying email: {str(e)}")
                    batch_results.append(self._fallback_classification(email_data))
            
            results.extend(batch_results)
            
            # Longer delay between batches
            if i + batch_size < len(emails_data):
                import time
                time.sleep(2)
        
        logger.info(f"Completed batch classification of {len(emails_data)} emails")
        return results
    
    def get_classification_stats(self, classifications: List[Dict]) -> Dict:
        """Generate statistics from classification results."""
        
        if not classifications:
            return {}
        
        stats = {
            'total_classified': len(classifications),
            'by_urgency': {'urgent': 0, 'high': 0, 'medium': 0, 'low': 0},
            'by_sender_type': {'estudiante': 0, 'profesor': 0, 'administracion': 0, 'externo': 0},
            'by_email_type': {'academico': 0, 'administrativo': 0, 'personal': 0, 'emergencia': 0},
            'avg_confidence': 0,
            'high_confidence_count': 0,
            'requires_immediate_action': 0
        }
        
        total_confidence = 0
        
        for classification in classifications:
            # Count by urgency
            urgency = classification.get('urgency_category', 'medium')
            if urgency in stats['by_urgency']:
                stats['by_urgency'][urgency] += 1
            
            # Count by sender type
            sender_type = classification.get('sender_type', 'externo')
            if sender_type in stats['by_sender_type']:
                stats['by_sender_type'][sender_type] += 1
            
            # Count by email type
            email_type = classification.get('email_type', 'academico')
            if email_type in stats['by_email_type']:
                stats['by_email_type'][email_type] += 1
            
            # Confidence stats
            confidence = classification.get('confidence_score', 0)
            total_confidence += confidence
            if confidence >= 0.8:
                stats['high_confidence_count'] += 1
            
            # Immediate action count
            if classification.get('requires_immediate_action', False):
                stats['requires_immediate_action'] += 1
        
        stats['avg_confidence'] = round(total_confidence / len(classifications), 3)
        stats['high_confidence_percentage'] = round((stats['high_confidence_count'] / len(classifications)) * 100, 1)
        
        return stats
    
    def suggest_response_priority(self, classification: Dict) -> Dict:
        """Suggest response timeframe based on classification."""
        
        urgency = classification.get('urgency_category', 'medium')
        sender_type = classification.get('sender_type', 'externo')
        email_type = classification.get('email_type', 'academico')
        
        suggestions = {
            'urgent': {
                'response_time': '15 minutos',
                'priority_level': 1,
                'suggested_action': 'Responder inmediatamente - posible emergencia estudiantil'
            },
            'high': {
                'response_time': '2 horas',
                'priority_level': 2,
                'suggested_action': 'Responder dentro del día - asunto académico importante'
            },
            'medium': {
                'response_time': '24 horas',
                'priority_level': 3,
                'suggested_action': 'Responder en horario laboral regular'
            },
            'low': {
                'response_time': '48 horas',
                'priority_level': 4,
                'suggested_action': 'Responder cuando sea conveniente'
            }
        }
        
        base_suggestion = suggestions.get(urgency, suggestions['medium'])
        
        # Adjust based on sender type
        if sender_type == 'estudiante' and urgency in ['medium', 'low']:
            base_suggestion['response_time'] = '12 horas'
            base_suggestion['suggested_action'] += ' (estudiante requiere atención prioritaria)'
        
        return base_suggestion