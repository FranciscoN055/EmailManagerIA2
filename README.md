# 📧 Email Manager IA

Sistema inteligente de gestión de correos con clasificación automática por urgencia usando IA para directores académicos.

## 🎯 Descripción del Proyecto

Email Manager IA es una solución completa que ayuda a directores académicos como Maritza Silva (ICIF) a gestionar hasta 200 correos diarios mediante:

- **Clasificación automática por IA** usando OpenAI GPT-4
- **Dashboard Kanban** tipo Trello con 5 categorías de urgencia
- **Integración con Microsoft Outlook** via Graph API
- **Interface profesional** con tema claro/oscuro

## 🏗️ Arquitectura del Sistema

```
📁 email-manager-ia/
├── 🎨 frontend/          # React + Material-UI + Vite
├── ⚙️  backend/          # Flask + PostgreSQL + OpenAI
├── 📋 README.md
├── 🐳 docker-compose.yml
└── 📄 .gitignore
```

## 🎨 Frontend (React)

### Tecnologías Implementadas
- **React 18** con Vite
- **Material-UI (MUI)** con tema personalizado Outlook
- **React Router** para navegación
- **React Query** para estado del servidor

### ✅ Características Completadas
- Dashboard Kanban con 5 columnas de urgencia
- Barra de estadísticas fija con progreso visual
- Sistema de tema claro/oscuro
- 50+ emails mock realistas para demo
- Cards de correo interactivas con hover effects
- Header fijo con búsqueda y filtros
- Responsive design para móviles

### Ejecutar Frontend
```bash
cd frontend
npm install
npm run dev
# Abre http://localhost:5175
```

## ⚙️ Backend (Flask)

### Tecnologías Configuradas
- **Flask 3.0** con factory pattern
- **PostgreSQL** con SQLAlchemy + UUID keys
- **Microsoft Graph API** para Outlook
- **OpenAI GPT-4** para clasificación
- **JWT** para autenticación
- **Celery + Redis** para tareas async

### Setup Backend
```bash
cd backend

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno (.env)
cp .env.example .env
# Editar .env con tus credenciales:
MICROSOFT_CLIENT_ID=tu-client-id-de-azure
MICROSOFT_CLIENT_SECRET=tu-client-secret-de-azure
OPENAI_API_KEY=tu-openai-key

# 3. Configurar base de datos
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 4. Ejecutar servidor
python run.py
# Abre http://127.0.0.1:5000
```

### 🔧 **Configuración Microsoft Graph API**

#### **1. Registrar App en Azure**
1. Ve a [Azure Portal](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps)
2. Click "New registration"
3. Nombre: `Email Manager IA`
4. Redirect URI: `http://localhost:5000/auth/microsoft/callback`
5. Copiar **Application ID** → `MICROSOFT_CLIENT_ID`
6. Generar **Client Secret** → `MICROSOFT_CLIENT_SECRET`

#### **2. Configurar Permisos API**
- `User.Read` - Leer perfil de usuario
- `Mail.ReadWrite` - Leer y escribir correos
- `Mail.Send` - Enviar correos
- `offline_access` - Refresh tokens

#### **3. Variables de Entorno Requeridas**
```env
MICROSOFT_CLIENT_ID=12345678-1234-1234-1234-123456789012
MICROSOFT_CLIENT_SECRET=abcXYZ123~secretvalue
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=http://localhost:5000/auth/microsoft/callback
```

## 🗄️ Categorías de Urgencia

1. 🔴 **Urgente** (próxima hora) - Rojo
2. 🟠 **Alta** (próximas 3 horas) - Naranja
3. 🟢 **Media** (hoy) - Verde
4. 🔵 **Baja** (mañana) - Azul
5. ⚪ **Procesados** - Gris

## 🚀 Estado Actual del Proyecto

### ✅ **COMPLETADO EN SESIONES PREVIAS**
- [x] **Frontend React completo** con dashboard Kanban funcional
- [x] **Backend Flask completo** with modelos de base de datos
- [x] **Sistema de temas** claro/oscuro
- [x] **Barra de progreso** interactiva y fija
- [x] **50+ emails mock** realistas para demo
- [x] **Estructura completa** de archivos y configuraciones
- [x] **Documentación** comprehensive

### 🆕 **COMPLETADO EN ESTA SESIÓN - Microsoft Graph Integration**
- [x] **Microsoft Graph Service completo** con MSAL authentication
- [x] **OAuth2 Flow implementado** - Login, callback, disconnect
- [x] **Email Synchronization API** - Sync desde Outlook con pagination
- [x] **Email Management endpoints** - CRUD operations y búsqueda
- [x] **Email Sending capabilities** - Envío de correos y respuestas
- [x] **Database Models actualizados** - Soporte para Microsoft tokens
- [x] **Environment templates** - Setup completo con .env.example
- [x] **API Testing completo** - Todos los endpoints funcionando

### 🔄 **PRÓXIMOS PASOS (Siguiente Sesión)**

#### **Fase 3: Clasificación con IA OpenAI**
1. Implementar OpenAI GPT-4 service completo
2. Prompts optimizados para clasificación académica
3. Batch processing de correos pendientes
4. Sistema de confidence scoring

#### **Fase 4: Frontend-Backend Integration**
1. Conectar React con Flask API endpoints
2. Implementar autenticación Microsoft en frontend
3. Reemplazar mock data con datos reales de Outlook
4. UI para sync, search, y reply functionality

#### **Fase 5: Production Deployment**
1. PostgreSQL setup y configuración
2. Docker compose para producción
3. Environment variables y secrets
4. Monitoring y logging

## 🎨 Capturas Actuales

**Dashboard funcional en**: `http://localhost:5175`
- ✅ 5 columnas Kanban con colores distintivos
- ✅ Cards de correo con información completa  
- ✅ Barra de progreso visual
- ✅ Header fijo con búsqueda y filtros
- ✅ Tema claro/oscuro intercambiable

**Backend API en**: `http://127.0.0.1:5000`
- ✅ Health check endpoint
- ✅ Estructura completa de modelos
- ✅ Microsoft Graph integration completa

### 🔗 **API Endpoints Disponibles**

#### **Microsoft Graph Authentication**
- `GET /api/microsoft/auth/login` - Iniciar OAuth2 flow
- `GET /api/microsoft/auth/callback` - Callback de Microsoft
- `POST /api/microsoft/auth/disconnect` - Desconectar cuenta
- `GET /api/microsoft/profile` - Obtener perfil de usuario
- `GET /api/microsoft/folders` - Obtener carpetas de correo

#### **Email Management**
- `POST /api/emails/sync` - Sincronizar correos desde Outlook
- `GET /api/emails/` - Listar correos con filtros y paginación
- `GET /api/emails/{id}` - Obtener detalles de correo específico
- `POST /api/emails/{id}/mark-read` - Marcar como leído
- `POST /api/emails/{id}/update-urgency` - Actualizar categoría de urgencia
- `POST /api/emails/{id}/reply` - Responder a correo específico
- `POST /api/emails/send` - Enviar nuevo correo
- `GET /api/emails/search?q=query` - Buscar correos
- `GET /api/emails/stats` - Estadísticas del dashboard

---

---

**Desarrollado con Claude Code (Sonnet 4)**  
**Sesión 1**: Frontend + Backend Structure ✅  
**Sesión 2**: Microsoft Graph Integration ✅