# 🚀 Guía de Despliegue - Email Manager IA

Esta guía te ayudará a desplegar tu aplicación Email Manager IA en servidores gratuitos.

## 📋 Requisitos Previos

1. **Cuenta de GitHub** (gratis)
2. **Cuenta de Railway** (gratis) - [railway.app](https://railway.app)
3. **Cuenta de Vercel** (gratis) - [vercel.com](https://vercel.com)
4. **Cuenta de Microsoft Azure** (gratis) - [azure.microsoft.com](https://azure.microsoft.com)

## 🎯 Arquitectura de Despliegue

```
Frontend (React) → Vercel
Backend (Flask)  → Railway
Base de datos    → Railway PostgreSQL
Autenticación    → Microsoft Graph API
```

## 🚀 Paso 1: Preparar el Código

### 1.1 Subir a GitHub
```bash
# Inicializar repositorio
git init
git add .
git commit -m "Initial commit"

# Crear repositorio en GitHub y subir
git remote add origin https://github.com/tu-usuario/email-manager-ia.git
git push -u origin main
```

## 🚀 Paso 2: Desplegar Backend en Railway

### 2.1 Crear cuenta en Railway
1. Ve a [railway.app](https://railway.app)
2. Inicia sesión con GitHub
3. Haz clic en "New Project"
4. Selecciona "Deploy from GitHub repo"
5. Conecta tu repositorio

### 2.2 Configurar Variables de Entorno
En Railway, ve a tu proyecto → Settings → Variables y agrega:

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=tu-secret-key-super-seguro-aqui
JWT_SECRET_KEY=tu-jwt-secret-key-super-seguro-aqui

# Microsoft Graph API
MICROSOFT_CLIENT_ID=tu-client-id-de-azure
MICROSOFT_CLIENT_SECRET=tu-client-secret-de-azure
MICROSOFT_TENANT_ID=tu-tenant-id-de-azure
MICROSOFT_REDIRECT_URI=https://tu-app.railway.app/auth/callback

# OpenAI (opcional)
OPENAI_API_KEY=tu-openai-api-key

# Base de datos (Railway la crea automáticamente)
DATABASE_URL=postgresql://... (Railway la proporciona)
```

### 2.3 Configurar Base de Datos
1. En Railway, haz clic en "New" → "Database" → "PostgreSQL"
2. Railway creará automáticamente la variable `DATABASE_URL`
3. Ejecuta las migraciones:
   ```bash
   railway run python -m flask db upgrade
   ```

## 🚀 Paso 3: Desplegar Frontend en Vercel

### 3.1 Crear cuenta en Vercel
1. Ve a [vercel.com](https://vercel.com)
2. Inicia sesión con GitHub
3. Haz clic en "New Project"
4. Importa tu repositorio

### 3.2 Configurar Variables de Entorno
En Vercel, ve a tu proyecto → Settings → Environment Variables:

```env
VITE_API_URL=https://tu-app.railway.app/api
```

### 3.3 Configurar Build Settings
- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

## 🔧 Paso 4: Configurar Azure App Registration

### 4.1 Actualizar URLs de Redirección
En tu Azure App Registration:

1. Ve a [portal.azure.com](https://portal.azure.com)
2. Azure Active Directory → App registrations
3. Selecciona tu aplicación
4. Authentication → Redirect URIs
5. Agrega: `https://tu-app.railway.app/auth/callback`

### 4.2 Verificar Permisos
Asegúrate de tener estos permisos:
- `Mail.ReadWrite` (Delegated)
- `Mail.Send` (Delegated)
- `User.Read` (Delegated)

## 🌐 Paso 5: Configurar Dominio Personalizado (Opcional)

### 5.1 En Railway
1. Ve a tu proyecto → Settings → Domains
2. Agrega tu dominio personalizado
3. Configura los registros DNS

### 5.2 En Vercel
1. Ve a tu proyecto → Settings → Domains
2. Agrega tu dominio personalizado
3. Configura los registros DNS

## 🔍 Paso 6: Verificar Despliegue

### 6.1 Backend
```bash
# Verificar que el backend esté funcionando
curl https://tu-app.railway.app/api/health
```

### 6.2 Frontend
1. Ve a tu URL de Vercel
2. Intenta hacer login con Microsoft
3. Verifica que funcione la autenticación

## 🛠️ Solución de Problemas

### Error de CORS
Si tienes errores de CORS, verifica que las URLs en `CORS_ORIGINS` coincidan con tu frontend.

### Error de Base de Datos
```bash
# Ejecutar migraciones
railway run python -m flask db upgrade
```

### Error de Variables de Entorno
Verifica que todas las variables estén configuradas correctamente en Railway.

## 📊 Monitoreo

### Railway
- Ve a tu dashboard para ver logs y métricas
- Configura alertas si es necesario

### Vercel
- Ve a tu dashboard para ver analytics
- Configura webhooks si es necesario

## 🔒 Seguridad

1. **Nunca** subas archivos `.env` al repositorio
2. Usa variables de entorno para todas las credenciales
3. Rota las claves regularmente
4. Usa HTTPS siempre

## 📈 Escalabilidad

### Railway
- Plan gratuito: 500 horas/mes
- Plan Pro: $5/mes para uso ilimitado

### Vercel
- Plan gratuito: 100GB bandwidth/mes
- Plan Pro: $20/mes para más recursos

## 🆘 Soporte

Si tienes problemas:
1. Revisa los logs en Railway/Vercel
2. Verifica las variables de entorno
3. Consulta la documentación de Railway/Vercel
4. Abre un issue en GitHub

---

¡Tu aplicación Email Manager IA estará funcionando en la nube! 🎉
