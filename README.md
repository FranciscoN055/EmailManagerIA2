# Email Manager IA

Sistema inteligente de gestión de correos con clasificación automática por urgencia usando IA.

## 🎯 Características Principales

- Conexión con cuentas Outlook múltiples
- Clasificación automática de correos por urgencia usando IA
- Organización en categorías temporales:
  - Responder en la próxima hora
  - Responder en las próximas 3 horas
  - Responder hoy
  - Responder mañana antes de X hrs

## 🛠️ Stack Tecnológico

- **Frontend**: React + Vite
- **Backend**: Python + Flask
- **Base de datos**: PostgreSQL
- **Containerización**: Docker
- **Control de versiones**: Git + GitHub

## 🚀 Instalación y Uso

### Prerrequisitos
- Node.js (v18+)
- Python (v3.11+)
- Docker y Docker Compose
- Git

### Configuración inicial
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/email-manager-ia.git
cd email-manager-ia

# Instalar dependencias del frontend
cd frontend
npm install

# Instalar dependencias del backend
cd ../backend
pip install -r requirements.txt

# Levantar servicios con Docker
docker-compose up -d
```

## 📁 Estructura del Proyecto

```
email-manager-ia/
├── frontend/                 # Aplicación React
├── backend/                  # API Flask
├── database/                # Configuración PostgreSQL
├── docker-compose.yml       # Orquestación de contenedores
└── docs/                    # Documentación
```

## 👥 Contribución

1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.