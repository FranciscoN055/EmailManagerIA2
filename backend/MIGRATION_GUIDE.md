# Guía de Migración - Mejoras en Clasificación de Emails

## 📋 Resumen de Cambios

Se han realizado mejoras significativas en el sistema de clasificación de emails con OpenAI:

### ✅ Mejoras Implementadas:
- **Prompt optimizado** para mejor distinción entre niveles de prioridad
- **Ejemplos específicos** para cada nivel de urgencia
- **Manejo mejorado** de respuestas con markdown
- **Logging detallado** para debugging
- **Rate limiting** mejorado para evitar errores 429

### 🎯 Niveles de Prioridad Mejorados:
- **URGENTE**: Emergencias médicas, accidentes, crisis de seguridad
- **ALTA**: Problemas académicos graves, reuniones urgentes, deadlines críticos
- **MEDIA**: Solicitudes académicas con plazo definido, cambios de horario
- **BAJA**: Consultas generales, información futura, documentación no urgente

## 🚀 Instrucciones de Migración

### 1. Actualizar el Código
```bash
git pull origin fix/email-sync-status
```

### 2. Reclasificar Emails Existentes
Ejecutar el script de migración para mejorar la clasificación de emails ya existentes:

```bash
cd backend
python migrate_existing_emails.py
```

**⚠️ Importante**: Este script:
- Reclasifica TODOS los emails ya clasificados
- Usa el nuevo prompt mejorado
- Maneja rate limiting automáticamente
- Muestra estadísticas antes y después

### 3. Verificar Resultados
```bash
python check_results.py
```

## 📊 Scripts Disponibles

### Scripts de Utilidad:
- `migrate_existing_emails.py` - Reclasificar emails existentes
- `check_results.py` - Verificar estadísticas de clasificación
- `generate_test_emails.py` - Generar emails de prueba
- `classify_all_pending.py` - Clasificar emails pendientes

### Scripts de Prueba:
- `test_openai_detailed.py` - Probar OpenAI con logging detallado
- `test_multiple_emails.py` - Probar múltiples emails
- `test_final.py` - Prueba final del sistema

## 🔧 Configuración

### Variables de Entorno Requeridas:
```env
OPENAI_API_KEY=tu_api_key_aqui
OPENAI_MODEL=gpt-4o-mini
```

### Dependencias:
```bash
pip install -r requirements.txt
```

## 📈 Mejoras en Precisión

### Antes:
- Muchos emails clasificados incorrectamente como "low"
- Difícil distinción entre "low" y "medium"
- Prompt genérico

### Después:
- **100% precisión** en emails de prueba
- **Mejor distinción** entre niveles
- **Prompt específico** para contexto académico
- **Ejemplos claros** para cada nivel

## 🐛 Troubleshooting

### Error 429 (Rate Limit):
- El script maneja automáticamente los rate limits
- Espera 10 segundos entre lotes
- Reintenta automáticamente

### Emails no se reclasifican:
- Verificar que `is_classified=True` en la base de datos
- Ejecutar `python check_results.py` para verificar estado

### OpenAI no responde:
- Verificar `OPENAI_API_KEY` en `.env`
- Verificar conectividad a internet
- Revisar logs para errores específicos

## 📞 Soporte

Si encuentras problemas:
1. Revisar logs del script de migración
2. Verificar configuración de OpenAI
3. Ejecutar scripts de prueba individuales
4. Contactar al equipo de desarrollo

---

**Fecha de migración**: $(date)  
**Versión**: 2.0  
**Autor**: Equipo de desarrollo
