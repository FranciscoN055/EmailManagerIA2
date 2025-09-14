# ✅ Checklist de Despliegue - Email Manager IA

## 📋 Lista de Verificación Paso a Paso

### 🔐 1. Configuración de Azure (15 minutos)

#### Crear App Registration
- [ ] Ir a [portal.azure.com](https://portal.azure.com)
- [ ] Buscar "App registrations"
- [ ] Crear nueva aplicación
- [ ] **Name**: `Email Manager IA`
- [ ] **Account types**: `Single tenant`
- [ ] **Redirect URI**: `Web` → `https://tu-dominio.vercel.app/auth/callback`

#### Configurar Permisos
- [ ] Ir a "API permissions"
- [ ] Agregar permisos de Microsoft Graph:
  - [ ] `User.Read`
  - [ ] `Mail.ReadWrite`
  - [ ] `Mail.Send`
  - [ ] `offline_access`
- [ ] Hacer clic en "Grant admin consent"

#### Obtener Credenciales
- [ ] Copiar **Application (client) ID**
- [ ] Copiar **Directory (tenant) ID**
- [ ] Crear **Client Secret** (24 meses)
- [ ] Copiar **Value** del secret

---

### 🖥️ 2. Despliegue del Backend en Render (20 minutos)

#### Preparar Código
- [ ] Verificar que `render.yaml` existe en la raíz
- [ ] Verificar que `requirements.txt` esté actualizado
- [ ] Verificar que `backend/run.py` existe

#### Crear Servicio en Render
- [ ] Ir a [render.com](https://render.com)
- [ ] Conectar con GitHub
- [ ] Crear "Web Service"
- [ ] **Name**: `email-manager-backend`
- [ ] **Environment**: `Python 3`
- [ ] **Root Directory**: `backend`
- [ ] **Build Command**: `pip install -r requirements.txt`
- [ ] **Start Command**: `python run.py`

#### Configurar Variables de Entorno
- [ ] `FLASK_ENV=production`
- [ ] `SECRET_KEY=[generar]`
- [ ] `JWT_SECRET_KEY=[generar]`
- [ ] `DATABASE_URL=[URL de PostgreSQL]`
- [ ] `MICROSOFT_CLIENT_ID=[de Azure]`
- [ ] `MICROSOFT_CLIENT_SECRET=[de Azure]`
- [ ] `MICROSOFT_TENANT_ID=[de Azure]`
- [ ] `MICROSOFT_REDIRECT_URI=https://tu-dominio-render.onrender.com/auth/callback`
- [ ] `OPENAI_API_KEY=[tu API key]`

#### Crear Base de Datos
- [ ] Crear "PostgreSQL" en Render
- [ ] **Name**: `email-manager-db`
- [ ] **Plan**: `Free`
- [ ] Copiar **External Database URL**
- [ ] Actualizar `DATABASE_URL` en variables de entorno

#### Inicializar Base de Datos
- [ ] Esperar a que el backend esté desplegado
- [ ] Visitar: `https://tu-dominio-render.onrender.com/api/init-db`
- [ ] Verificar mensaje de éxito
- [ ] Verificar que se crearon las tablas

#### Detener Servicios en Render
- [ ] Ir a [render.com/dashboard](https://render.com/dashboard)
- [ ] Buscar servicio `email-manager-backend`
- [ ] Ir a "Settings" → "Suspend Service" para detener
- [ ] Ir a "Settings" → "Resume Service" para reactivar
- [ ] Buscar base de datos `email-manager-db`
- [ ] Ir a "Settings" → "Suspend Database" para detener
- [ ] Ir a "Settings" → "Resume Database" para reactivar
- [ ] Para eliminar: "Settings" → "Delete Service/Database"

---

### 🌐 3. Despliegue del Frontend en Vercel (15 minutos)

#### Preparar Código
- [ ] Verificar que `vercel.json` existe en la raíz
- [ ] Verificar que `.vercelignore` existe
- [ ] Verificar que `frontend/package.json` existe

#### Crear Proyecto en Vercel
- [ ] Ir a [vercel.com](https://vercel.com)
- [ ] Conectar con GitHub
- [ ] Importar repositorio
- [ ] **Framework Preset**: `Vite`
- [ ] **Root Directory**: `frontend`
- [ ] **Build Command**: `npm run build`
- [ ] **Output Directory**: `dist`

#### Configurar Variables de Entorno
- [ ] Ir a "Settings" → "Environment Variables"
- [ ] Agregar: `VITE_API_URL=https://tu-dominio-render.onrender.com`

#### Desplegar
- [ ] Hacer clic en "Deploy"
- [ ] Esperar build (2-3 minutos)
- [ ] Copiar URL de Vercel

#### Controlar Servicios en Vercel
- [ ] **IMPORTANTE**: Vercel no "detiene" como Render, solo controla nuevos deployments
- [ ] Ir a [vercel.com/dashboard](https://vercel.com/dashboard)
- [ ] Buscar proyecto `email-manager-ia`
- [ ] Ir a "Settings" → "General"
- [ ] Buscar sección "Vercel Toolbar"
- [ ] Cambiar "Production Deployments" a **OFF** (evita nuevos deployments)
- [ ] Cambiar "Pre-production Deployments" a **OFF** (opcional)
- [ ] Cambiar "Production Deployments" a **ON** para reactivar deployments
- [ ] **Alternativa: Cancelar deployment**: Durante construcción → "Cancel" para detener
- [ ] Para eliminar deployment: "Deployments" → tres puntos (...) → "Delete"
- [ ] Para eliminar proyecto: "Settings" → "Danger Zone" → "Delete Project"

---

### 🔗 4. Configuración de Integración (10 minutos)

#### Actualizar Azure Redirect URIs
- [ ] Ir a Azure Portal → App registrations
- [ ] Ir a "Authentication"
- [ ] Agregar redirect URI: `https://tu-dominio-vercel.vercel.app/auth/callback`
- [ ] Agregar redirect URI: `https://tu-dominio-render.onrender.com/auth/callback`
- [ ] Guardar cambios

#### Verificar CORS en Backend
- [ ] Verificar que `CORS_ORIGINS` incluya la URL de Vercel
- [ ] Verificar que `MICROSOFT_REDIRECT_URI` sea correcta

---

### ✅ 5. Verificación y Pruebas (15 minutos)

#### Verificar Backend
- [ ] Health check: `https://tu-dominio-render.onrender.com/api/health`
- [ ] Debug info: `https://tu-dominio-render.onrender.com/api/debug`
- [ ] Verificar que `environment: production`
- [ ] Verificar que `database_url` sea PostgreSQL

#### Verificar Frontend
- [ ] Visitar URL de Vercel
- [ ] Verificar que se conecte al backend
- [ ] Verificar que no haya errores en consola

#### Verificar Integración
- [ ] Hacer clic en "Iniciar Sesión"
- [ ] Verificar redirección a Microsoft
- [ ] Autorizar permisos
- [ ] Verificar que regrese a la aplicación
- [ ] Verificar que se muestre el dashboard

#### Verificar Funcionalidad de Emails
- [ ] Hacer clic en "Sincronizar Emails"
- [ ] Verificar que se descarguen emails
- [ ] Hacer clic en "Responder" en un email
- [ ] Verificar que se abra el modal
- [ ] Verificar que se muestre el contenido del email
- [ ] Escribir una respuesta de prueba
- [ ] Enviar la respuesta
- [ ] Verificar que se envíe correctamente

---

### 🚨 6. Solución de Problemas Comunes

#### Error: "No such table: users"
- [ ] Visitar `/api/init-db` para inicializar la base de datos
- [ ] Verificar que `DATABASE_URL` esté configurado correctamente

#### Error: "AADSTS50011: Redirect URI mismatch"
- [ ] Verificar que las URIs en Azure coincidan exactamente
- [ ] Verificar que no haya espacios extra
- [ ] Verificar que use `https://` no `http://`

#### Error: "Error al conectar con Microsoft"
- [ ] Verificar que `VITE_API_URL` esté configurado
- [ ] Verificar que el backend esté funcionando
- [ ] Verificar CORS en el backend

#### Error: "psycopg2 not available"
- [ ] Verificar que `psycopg2-binary==2.9.10` esté en `requirements.txt`
- [ ] Verificar que `pythonVersion: "3.11"` esté en `render.yaml`

#### Error: "ModuleNotFoundError: No module named 'email_validator'"
- [ ] Agregar `email-validator==2.1.0` a `requirements.txt`
- [ ] Redesplegar el backend

---

### 📊 7. Verificación Final

#### URLs Importantes
- [ ] **Frontend**: `https://tu-dominio-vercel.vercel.app`
- [ ] **Backend**: `https://tu-dominio-render.onrender.com`
- [ ] **Health Check**: `https://tu-dominio-render.onrender.com/api/health`
- [ ] **Init DB**: `https://tu-dominio-render.onrender.com/api/init-db`

#### Funcionalidades Verificadas
- [ ] Login con Microsoft
- [ ] Sincronización de emails
- [ ] Clasificación de emails
- [ ] Modal de respuesta
- [ ] Envío de respuestas
- [ ] Interfaz responsive

#### Performance
- [ ] Tiempo de carga del frontend < 3 segundos
- [ ] Tiempo de respuesta del backend < 2 segundos
- [ ] Sincronización de emails < 30 segundos

### 🔧 8. Gestión de Servicios

#### Controlar Servicios
- [ ] **Render Backend**: Dashboard → Settings → Suspend/Resume Service (detiene completamente)
- [ ] **Render Database**: Dashboard → Settings → Suspend/Resume Database (detiene completamente)
- [ ] **Vercel Frontend**: Dashboard → Settings → General → Vercel Toolbar → Production Deployments ON/OFF (solo controla nuevos deployments)

#### Eliminar Servicios Completamente
- [ ] **Render**: Settings → Delete Service/Database
- [ ] **Vercel**: Settings → Danger Zone → Delete Project

#### Monitoreo de Servicios
- [ ] **Render**: Dashboard → Logs para ver errores
- [ ] **Vercel**: Dashboard → Functions → Logs
- [ ] **Azure**: Portal → App registrations → Monitoring

---

### 🎯 8. Documentación para el Equipo

#### Archivos de Configuración
- [ ] `DEPLOYMENT_GUIDE.md` - Guía completa
- [ ] `DEPLOYMENT_CHECKLIST.md` - Esta lista
- [ ] `README.md` - Documentación del proyecto
- [ ] `backend/env.example` - Variables de entorno de ejemplo

#### Información de Acceso
- [ ] URLs de producción documentadas
- [ ] Credenciales de Azure documentadas (sin valores)
- [ ] Variables de entorno documentadas
- [ ] Proceso de actualización documentado

---

## 🚀 ¡Despliegue Completado!

Si todos los elementos están marcados, tu aplicación Email Manager IA está desplegada y funcionando correctamente.

### Próximos Pasos
1. **Monitoreo**: Revisar logs regularmente
2. **Actualizaciones**: Seguir el proceso de Git → Deploy
3. **Mantenimiento**: Verificar que los servicios estén activos
4. **Backup**: La base de datos se respalda automáticamente

### Contacto de Soporte
- **Issues**: Crear issue en GitHub
- **Documentación**: Ver archivos `.md` del proyecto
- **Logs**: Revisar dashboards de Vercel y Render

---

*Checklist creado para Email Manager IA v1.0.0*
*Última actualización: $(date)*
