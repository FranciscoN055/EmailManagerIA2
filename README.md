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
MICROSOFT_CLIENT_ID=tu-client-id
MICROSOFT_CLIENT_SECRET=tu-client-secret
OPENAI_API_KEY=tu-openai-key

# 3. Configurar base de datos
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 4. Ejecutar servidor
python run.py
# Abre http://127.0.0.1:5000
```

## 🗄️ Categorías de Urgencia

1. 🔴 **Urgente** (próxima hora) - Rojo
2. 🟠 **Alta** (próximas 3 horas) - Naranja
3. 🟢 **Media** (hoy) - Verde
4. 🔵 **Baja** (mañana) - Azul
5. ⚪ **Procesados** - Gris

## 🚀 Estado Actual del Proyecto

### ✅ **COMPLETADO EN ESTA SESIÓN**
- [x] **Frontend React completo** con dashboard Kanban funcional
- [x] **Backend Flask completo** with modelos de base de datos
- [x] **Sistema de temas** claro/oscuro
- [x] **Barra de progreso** interactiva y fija
- [x] **50+ emails mock** realistas para demo
- [x] **Estructura completa** de archivos y configuraciones
- [x] **Documentación** comprehensive

### 🔄 **PRÓXIMOS PASOS (Siguiente Sesión)**

#### **Fase 2: Integración Microsoft Graph**
1. Implementar autenticación OAuth2
2. Sincronización de correos desde Outlook  
3. API endpoints para conexión de cuentas

#### **Fase 3: Clasificación con IA**
1. Prompts optimizados para OpenAI GPT-4
2. Lógica de clasificación por urgencia
3. Procesamiento en lotes de correos

#### **Fase 4: Integración Frontend-Backend**
1. Conectar React con Flask API
2. Reemplazar mock data con datos reales
3. Autenticación en frontend

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
- ✅ Configuración de APIs listas

---

**Desarrollado con Claude Code (Sonnet 4) - Sesión 1 Completada** ✅