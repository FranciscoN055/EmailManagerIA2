# Changelog - Feature Branch: email-writing-and-deployment

## 🚀 Nuevas Funcionalidades Añadidas

### 📸 **Funcionalidad de Foto de Perfil y Siglas**
- **Archivos modificados:**
  - `backend/app/routes/microsoft.py` - Nuevo endpoint `/profile/photo`
  - `backend/app/services/microsoft_graph.py` - Método `get_user_photo()`
  - `frontend/src/pages/Dashboard.jsx` - Lógica para mostrar foto/siglas

- **Características:**
  - ✅ Muestra foto de perfil desde Microsoft Graph si está disponible
  - ✅ Genera siglas automáticamente del nombre del usuario
  - ✅ Fallback inteligente: foto → siglas → "??"
  - ✅ Función `getInitials()` para generar siglas de nombre/email

### 🤖 **Indicador de Confianza de IA**
- **Archivos modificados:**
  - `frontend/src/components/email/EmailCard.jsx` - Chip de confianza con colores
  - `backend/app/routes/emails.py` - Campo `ai_confidence` en respuestas API
  - `frontend/src/pages/Dashboard.jsx` - Mapeo correcto del campo

- **Características:**
  - ✅ Muestra porcentaje de confianza de la IA (0-100%)
  - ✅ Código de colores según confianza:
    - 🟢 Verde (≥80%): Alta confianza
    - 🟠 Naranja (60-79%): Confianza media
    - 🔴 Rojo (<60%): Baja confianza
    - ⚫ Gris (undefined): Sin datos
  - ✅ Manejo robusto de valores undefined/null

## 🔧 **Correcciones Técnicas**
- Arreglado mapeo de campo `confidence_score` → `ai_confidence` en API
- Mejorada función `getConfidenceColor()` con lógica de colores
- Añadido soporte para Microsoft Graph Photo API

## 📝 **Notas de Implementación**
- Los cambios son compatibles con la estructura existente de la base de datos
- No se requieren migraciones adicionales (campo `profile_picture_url` ya existe)
- La funcionalidad de foto es opcional y no afecta el funcionamiento si no hay foto disponible

---
*Última actualización: $(date)*
