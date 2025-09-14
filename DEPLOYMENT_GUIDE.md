# 🚀 Guía de Despliegue - Email Manager IA

Esta guía explica cómo desplegar la aplicación Email Manager IA en Vercel (frontend) y Render (backend) de forma gratuita.

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración de Azure](#configuración-de-azure)
3. [Despliegue del Backend (Render)](#despliegue-del-backend-render)
4. [Despliegue del Frontend (Vercel)](#despliegue-del-frontend-vercel)
5. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
6. [Verificación y Pruebas](#verificación-y-pruebas)
7. [Solución de Problemas](#solución-de-problemas)
8. [Mantenimiento](#mantenimiento)

---

## 🔧 Requisitos Previos

### Herramientas Necesarias
- [Git](https://git-scm.com/) instalado
- Cuenta de [GitHub](https://github.com/)
- Cuenta de [Vercel](https://vercel.com/) (gratuita)
- Cuenta de [Render](https://render.com/) (gratuita)
- Cuenta de [Microsoft Azure](https://azure.microsoft.com/) (gratuita)

### Estructura del Proyecto
```
email-manager-ia/
├── frontend/          # React + Vite
├── backend/           # Flask + Python
├── render.yaml        # Configuración de Render
└── README.md
```

---

## 🔐 Configuración de Azure

### 1. Crear App Registration en Azure

1. **Acceder a Azure Portal**
   - Ve a [portal.azure.com](https://portal.azure.com)
   - Inicia sesión con tu cuenta Microsoft

2. **Crear App Registration**
   - Busca "App registrations" en el buscador
   - Haz clic en "New registration"
   - **Name**: `Email Manager IA`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: `Web` → `https://tu-dominio-vercel.vercel.app/auth/callback`
   - Haz clic en "Register"

3. **Configurar Permisos**
   - Ve a "API permissions"
   - Haz clic en "Add a permission"
   - Selecciona "Microsoft Graph"
   - Selecciona "Delegated permissions"
   - Agrega estos permisos:
     - `User.Read`
     - `Mail.ReadWrite`
     - `Mail.Send`
     - `offline_access`
   - Haz clic en "Grant admin consent"

4. **Obtener Credenciales**
   - Ve a "Overview"
   - Copia el **Application (client) ID**
   - Copia el **Directory (tenant) ID**
   - Ve a "Certificates & secrets"
   - Haz clic en "New client secret"
   - **Description**: `Email Manager Secret`
   - **Expires**: `24 months`
   - Copia el **Value** (solo se muestra una vez)

### 2. Configurar Redirect URIs

**URIs de Redirección Necesarios:**
```
https://tu-dominio-vercel.vercel.app/auth/callback
https://tu-dominio-render.onrender.com/auth/callback
http://localhost:5173/auth/callback (para desarrollo)
```

---

## 🖥️ Despliegue del Backend (Render)

### 1. Preparar el Código

1. **Crear archivo `render.yaml`** (ya existe en el proyecto):
```yaml
services:
  - type: web
    name: email-manager-backend
    env: python
    plan: free
    pythonVersion: "3.11"
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python run.py"
    healthCheckPath: "/api/health"
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        value: postgresql://usuario:password@host:puerto/database
      - key: MICROSOFT_CLIENT_ID
        sync: false
      - key: MICROSOFT_CLIENT_SECRET
        sync: false
      - key: MICROSOFT_TENANT_ID
        sync: false
      - key: MICROSOFT_REDIRECT_URI
        sync: false
      - key: OPENAI_API_KEY
        sync: false

  - type: pserv
    name: email-manager-db
    env: postgresql
    plan: free
```

### 2. Desplegar en Render

1. **Conectar con GitHub**
   - Ve a [render.com](https://render.com)
   - Inicia sesión con GitHub
   - Haz clic en "New +" → "Web Service"
   - Conecta tu repositorio de GitHub

2. **Configurar el Servicio**
   - **Name**: `email-manager-backend`
   - **Environment**: `Python 3`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`

3. **Configurar Variables de Entorno**
   - Ve a "Environment" en el dashboard
   - Agrega estas variables:
     ```
     FLASK_ENV=production
     SECRET_KEY=[generar automáticamente]
     JWT_SECRET_KEY=[generar automáticamente]
     DATABASE_URL=[URL de PostgreSQL de Render]
     MICROSOFT_CLIENT_ID=[tu client ID de Azure]
     MICROSOFT_CLIENT_SECRET=[tu client secret de Azure]
     MICROSOFT_TENANT_ID=[tu tenant ID de Azure]
     MICROSOFT_REDIRECT_URI=https://tu-dominio-render.onrender.com/auth/callback
     OPENAI_API_KEY=[tu API key de OpenAI]
     ```

4. **Crear Base de Datos PostgreSQL**
   - En el dashboard de Render, haz clic en "New +" → "PostgreSQL"
   - **Name**: `email-manager-db`
   - **Plan**: `Free`
   - **Region**: `Oregon (US West)`
   - Copia la **External Database URL**

5. **Inicializar la Base de Datos**
   - Una vez desplegado, ve a tu URL de Render
   - Visita: `https://tu-dominio-render.onrender.com/api/init-db`
   - Deberías ver un mensaje de éxito con las tablas creadas

### 3. Detener Servicios en Render

#### Detener Backend (Web Service)
1. **Ir al Dashboard de Render**
   - Ve a [render.com/dashboard](https://render.com/dashboard)
   - Busca tu servicio `email-manager-backend`

2. **Detener el Servicio**
   - Haz clic en el nombre del servicio
   - Ve a la pestaña "Settings"
   - Haz clic en "Suspend Service"
   - Confirma la suspensión

3. **Reactivar el Servicio**
   - En la misma página, haz clic en "Resume Service"
   - El servicio se reactivará automáticamente

#### Detener Base de Datos (PostgreSQL)
1. **Ir al Dashboard de Render**
   - Busca tu base de datos `email-manager-db`

2. **Detener la Base de Datos**
   - Haz clic en el nombre de la base de datos
   - Ve a la pestaña "Settings"
   - Haz clic en "Suspend Database"
   - Confirma la suspensión

3. **Reactivar la Base de Datos**
   - En la misma página, haz clic en "Resume Database"
   - La base de datos se reactivará automáticamente

#### Eliminar Servicios Completamente
1. **Eliminar Web Service**
   - Ve a "Settings" del servicio
   - Haz clic en "Delete Service"
   - Escribe el nombre del servicio para confirmar

2. **Eliminar Base de Datos**
   - Ve a "Settings" de la base de datos
   - Haz clic en "Delete Database"
   - Escribe el nombre de la base de datos para confirmar

---

## 🌐 Despliegue del Frontend (Vercel)

### 1. Preparar el Código

1. **Crear archivo `vercel.json`** en la raíz del proyecto:
```json
{
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
```

2. **Crear archivo `.vercelignore`** en la raíz:
```
backend/
node_modules/
.git/
*.log
```

### 2. Desplegar en Vercel

1. **Conectar con GitHub**
   - Ve a [vercel.com](https://vercel.com)
   - Inicia sesión con GitHub
   - Haz clic en "New Project"
   - Importa tu repositorio de GitHub

2. **Configurar el Proyecto**
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

3. **Configurar Variables de Entorno**
   - Ve a "Settings" → "Environment Variables"
   - Agrega:
     ```
     VITE_API_URL=https://tu-dominio-render.onrender.com
     ```

4. **Desplegar**
   - Haz clic en "Deploy"
   - Espera a que termine el build (2-3 minutos)
   - Obtén tu URL de Vercel

### 5. Detener Servicios en Vercel

#### Controlar Frontend (Web App)

**⚠️ IMPORTANTE**: Vercel no "detiene" el servicio como Render. Solo controla los **nuevos deployments**. El sitio sigue funcionando con el último deployment.

1. **Ir al Dashboard de Vercel**
   - Ve a [vercel.com/dashboard](https://vercel.com/dashboard)
   - Busca tu proyecto `email-manager-ia`

2. **Prevenir Nuevos Deployments**
   - Haz clic en el nombre del proyecto
   - Ve a la pestaña "Settings"
   - Haz clic en "General"
   - Busca la sección "Vercel Toolbar"
   - Cambia "Production Deployments" a **OFF** (evita nuevos deployments)
   - Cambia "Pre-production Deployments" a **OFF** (opcional)
   - Los cambios se guardan automáticamente

3. **Reactivar Deployments**
   - En la misma página, cambia "Production Deployments" a **ON**
   - Los nuevos cambios se desplegarán automáticamente

#### Cancelar Deployment en Progreso
1. **Durante la Construcción**
   - Cuando Vercel inicie un nuevo deployment
   - Te redirigirá automáticamente a la página de construcción
   - Verás el progreso del build en tiempo real

2. **Cancelar el Proceso**
   - Busca el botón "Cancel" en la página de construcción
   - Haz clic en "Cancel" para detener el deployment
   - El sitio quedará con el último deployment exitoso

#### Eliminar Deployment Específico
1. **Ir a la pestaña "Deployments"**
   - Haz clic en el nombre del proyecto
   - Ve a la pestaña "Deployments"
   - Busca el deployment que quieres eliminar

2. **Eliminar Deployment**
   - Haz clic en los tres puntos (...) del deployment
   - Selecciona "Delete" para eliminar ese deployment
   - **Nota**: Solo puedes eliminar deployments individuales, no el proyecto completo

#### Alternativa: Cancelar Deployment
1. **Cancelar Deployment en Progreso**
   - Cuando Vercel inicie un nuevo deployment
   - Ve a la página de construcción del deployment
   - Haz clic en "Cancel" para detener el proceso
   - El sitio quedará con el último deployment exitoso

2. **Resultado**
   - El sitio sigue activo con el último deployment
   - No se aplican los cambios nuevos
   - Perfecto para detener cambios no deseados

#### Alternativa: Usar Dominio Personalizado
1. **Configurar Dominio Personalizado**
   - Ve a "Settings" → "Domains"
   - Agrega un dominio personalizado
   - Cambia el DNS para apuntar a otro lugar

2. **Redirigir Tráfico**
   - Usa el dominio personalizado para redirigir a otra página
   - O apunta a un sitio de "mantenimiento"

#### Eliminar Proyecto Completamente
1. **Eliminar Proyecto**
   - Ve a "Settings" del proyecto
   - Haz clic en "General"
   - Busca la sección "Danger Zone"
   - Haz clic en "Delete Project"
   - Escribe el nombre del proyecto para confirmar

#### Detener Dominio Personalizado
1. **Ir a la pestaña "Domains"**
   - Ve a "Settings" → "Domains"
   - Busca tu dominio personalizado

2. **Eliminar Dominio**
   - Haz clic en el botón de eliminar junto al dominio
   - Confirma la eliminación

---

## ⚙️ Configuración de Variables de Entorno

### Backend (Render)
```bash
FLASK_ENV=production
SECRET_KEY=[generar automáticamente]
JWT_SECRET_KEY=[generar automáticamente]
DATABASE_URL=postgresql://usuario:password@host:puerto/database
MICROSOFT_CLIENT_ID=[tu client ID de Azure]
MICROSOFT_CLIENT_SECRET=[tu client secret de Azure]
MICROSOFT_TENANT_ID=[tu tenant ID de Azure]
MICROSOFT_REDIRECT_URI=https://tu-dominio-render.onrender.com/auth/callback
OPENAI_API_KEY=[tu API key de OpenAI]
```

### Frontend (Vercel)
```bash
VITE_API_URL=https://tu-dominio-render.onrender.com
```

### Azure App Registration
```
Redirect URIs:
- https://tu-dominio-vercel.vercel.app/auth/callback
- https://tu-dominio-render.onrender.com/auth/callback
- http://localhost:5173/auth/callback
```

---

## ✅ Verificación y Pruebas

### 1. Verificar Backend
```bash
# Health check
curl https://tu-dominio-render.onrender.com/api/health

# Debug info
curl https://tu-dominio-render.onrender.com/api/debug

# Inicializar base de datos
curl https://tu-dominio-render.onrender.com/api/init-db
```

### 2. Verificar Frontend
- Visita tu URL de Vercel
- Verifica que se conecte al backend
- Prueba el login con Microsoft
- Prueba la funcionalidad de emails

### 3. Verificar Integración
- Inicia sesión en la aplicación
- Sincroniza emails
- Prueba responder a un correo
- Verifica que se envíen correctamente

---

## 🔧 Solución de Problemas

### Error: "No such table: users"
**Solución**: Inicializar la base de datos
```bash
curl https://tu-dominio-render.onrender.com/api/init-db
```

### Error: "AADSTS50011: Redirect URI mismatch"
**Solución**: Verificar que las URIs en Azure coincidan exactamente con las URLs de producción

### Error: "Error al conectar con Microsoft"
**Solución**: 
1. Verificar que `VITE_API_URL` esté configurado correctamente
2. Verificar que el backend esté funcionando
3. Verificar CORS en el backend

### Error: "psycopg2 not available"
**Solución**: Verificar que `psycopg2-binary==2.9.10` esté en `requirements.txt`

### Error: "ModuleNotFoundError: No module named 'email_validator'"
**Solución**: Agregar `email-validator==2.1.0` a `requirements.txt`

---

## 🔄 Mantenimiento

### Actualizaciones de Código
1. **Hacer cambios** en tu repositorio local
2. **Commit y push** a GitHub:
   ```bash
   git add .
   git commit -m "Descripción del cambio"
   git push origin main
   ```
3. **Vercel** se actualiza automáticamente
4. **Render** se actualiza automáticamente

### Monitoreo
- **Vercel**: Dashboard → Analytics
- **Render**: Dashboard → Metrics
- **Azure**: Portal → App registrations → Monitoring

### Logs
- **Vercel**: Dashboard → Functions → Logs
- **Render**: Dashboard → Logs
- **Backend**: Logs en la consola de Render

### Backup de Base de Datos
- **Render**: Automático (plan gratuito incluye backup)
- **Manual**: Exportar desde el dashboard de Render

---

## 📞 Soporte

### Recursos Útiles
- [Documentación de Vercel](https://vercel.com/docs)
- [Documentación de Render](https://render.com/docs)
- [Documentación de Microsoft Graph](https://docs.microsoft.com/en-us/graph/)
- [Documentación de Azure AD](https://docs.microsoft.com/en-us/azure/active-directory/)

### Contacto
- **Issues**: Crear un issue en GitHub
- **Documentación**: Ver `README.md` del proyecto
- **Configuración**: Ver `backend/env.example`

---

## 🎯 Checklist de Despliegue

### Pre-despliegue
- [ ] Código subido a GitHub
- [ ] Azure App Registration configurado
- [ ] Variables de entorno preparadas
- [ ] `render.yaml` configurado
- [ ] `vercel.json` configurado

### Despliegue
- [ ] Backend desplegado en Render
- [ ] Base de datos PostgreSQL creada
- [ ] Base de datos inicializada (`/api/init-db`)
- [ ] Frontend desplegado en Vercel
- [ ] Variables de entorno configuradas

### Post-despliegue
- [ ] Health check del backend
- [ ] Conexión frontend-backend
- [ ] Login con Microsoft funcionando
- [ ] Sincronización de emails
- [ ] Envío de respuestas funcionando

---

## 📝 Notas Importantes

1. **Plan Gratuito**: Tanto Vercel como Render tienen límites en el plan gratuito
2. **Sleep Mode**: Render puede "dormir" después de 15 minutos de inactividad
3. **CORS**: Asegúrate de que las URLs estén en la configuración de CORS
4. **Tokens**: Los tokens de Microsoft expiran, el usuario debe reconectarse
5. **Base de Datos**: La inicialización es manual, no automática

---

*Última actualización: $(date)*
*Versión: 1.0.0*
