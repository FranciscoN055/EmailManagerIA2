# Guía de Colaboración - Email Manager IA

## 🚀 Configuración Inicial para Colaboradores

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd email-manager-ia
```

### 2. Configurar Variables de Entorno
**¡IMPORTANTE!** Nunca subas archivos `.env` con tus API keys reales.

#### Backend:
```bash
cd backend
cp .env.example .env
# Edita .env con tus propias API keys
```

#### Frontend:
```bash
cd frontend  
cp .env.example .env
# Edita .env si es necesario
```

### 3. Obtener API Keys
- **Microsoft Graph API**: [Azure Portal](https://portal.azure.com)
- **OpenAI API**: [OpenAI Platform](https://platform.openai.com)

### 4. Instalar Dependencias
#### Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend:
```bash
cd frontend
npm install
```

### 5. Ejecutar el Proyecto
#### Backend (terminal 1):
```bash
cd backend
python -m flask run --debug --port=5000
```

#### Frontend (terminal 2):
```bash
cd frontend
npm run dev
```

## 🔒 Trabajo en Equipo Seguro

### Flujo de Trabajo con Ramas
1. **Nunca trabajar directamente en `main`**
2. **Siempre crear una rama nueva**:
   ```bash
   git checkout -b feature/tu-nueva-funcionalidad
   ```
3. **Hacer commits descriptivos**:
   ```bash
   git add .
   git commit -m "feat: descripción clara del cambio"
   ```
4. **Subir tu rama**:
   ```bash
   git push origin feature/tu-nueva-funcionalidad
   ```
5. **Crear Pull Request** en GitHub
6. **Esperar revisión** antes de hacer merge

### Tipos de Commits
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bugs
- `docs:` Documentación
- `style:` Formato de código
- `refactor:` Refactorización
- `test:` Pruebas

## ⚠️ Reglas Importantes

### ❌ NO HACER:
- Subir archivos `.env` con API keys reales
- Hacer push directamente a `main`
- Commitear `node_modules/` o `venv/`
- Subir archivos de base de datos (*.db)

### ✅ SÍ HACER:
- Usar ramas para cada funcionalidad
- Hacer commits pequeños y frecuentes
- Revisar el código antes de hacer push
- Actualizar `.env.example` si agregaste nuevas variables

## 🆘 Problemas Comunes

### Error de puerto ocupado:
```bash
# Windows
netstat -ano | findstr :5178
taskkill /PID <número> /F

# Linux/Mac  
lsof -i :5178
kill -9 <PID>
```

### Error de dependencias:
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### Error de variables de entorno:
- Verifica que el archivo `.env` existe
- Asegúrate que las API keys son válidas
- Reinicia los servicios después de cambiar `.env`

## 📞 Ayuda
Si tienes problemas, crea un issue en GitHub o contacta al equipo.