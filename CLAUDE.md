- Fase 3: OpenAI Integration - Clasificación Inteligente de Correos

## Objetivo
Implementar clasificación automática de correos usando OpenAI GPT-4, optimizada para el contexto de una directora académica.

## Archivos a crear:

### 1. app/services/openai_service.py
Servicio completo para:
- Clasificación de urgencia por contexto académico
- Prompts especializados para Universidad San Sebastián
- Batch processing de múltiples correos
- Sistema de confidence scoring
- Detección de patrones (reuniones, deadlines, emergencias)

### 2. Integrar clasificación automática en:
- /api/emails/sync - Clasificar automáticamente al sincronizar
- /api/emails/classify - Endpoint para reclasificar correos
- /api/emails/batch-process - Procesar correos pendientes

### 3. Contexto académico específico:
- Identificar correos de estudiantes vs profesores vs administración
- Detectar deadlines académicos (exámenes, entregas, reuniones)
- Reconocer emergencias estudiantiles
- Clasificar por tipo: académico, administrativo, personal

### 4. Prompts optimizados:
- Considerar el rol de directora de carrera ICIF
- Patrones típicos de correos universitarios
- Terminología académica en español
- Clasificación en 4 niveles: Urgente, Alta, Media, Baja

Implementar sistema completo de clasificación IA que transforme los correos sincronizados en un dashboard inteligente y contextualizado.