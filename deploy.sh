#!/bin/bash

# 🚀 Script de Despliegue Automatizado - Email Manager IA
# Este script te ayuda a desplegar tu aplicación paso a paso

echo "🚀 Iniciando despliegue de Email Manager IA..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si git está inicializado
if [ ! -d ".git" ]; then
    print_status "Inicializando repositorio Git..."
    git init
    git add .
    git commit -m "Initial commit"
    print_success "Repositorio Git inicializado"
else
    print_success "Repositorio Git ya existe"
fi

# Verificar si hay cambios sin commitear
if [ -n "$(git status --porcelain)" ]; then
    print_warning "Hay cambios sin commitear. ¿Quieres commitearlos? (y/n)"
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        git add .
        git commit -m "Deploy commit $(date)"
        print_success "Cambios commiteados"
    fi
fi

# Verificar si Railway CLI está instalado
if ! command -v railway &> /dev/null; then
    print_warning "Railway CLI no está instalado. Instalando..."
    npm install -g @railway/cli
    print_success "Railway CLI instalado"
fi

# Verificar si Vercel CLI está instalado
if ! command -v vercel &> /dev/null; then
    print_warning "Vercel CLI no está instalado. Instalando..."
    npm install -g vercel
    print_success "Vercel CLI instalado"
fi

print_status "Verificando archivos de configuración..."

# Verificar archivos necesarios
required_files=("Procfile" "railway.json" "nixpacks.toml" "frontend/vercel.json")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "✓ $file existe"
    else
        print_error "✗ $file no existe"
        exit 1
    fi
done

print_status "Archivos de configuración verificados"

echo ""
echo "🎯 Próximos pasos manuales:"
echo ""
echo "1. 📝 Subir código a GitHub:"
echo "   git remote add origin https://github.com/tu-usuario/email-manager-ia.git"
echo "   git push -u origin main"
echo ""
echo "2. 🚂 Desplegar backend en Railway:"
echo "   - Ve a https://railway.app"
echo "   - Conecta tu repositorio de GitHub"
echo "   - Configura las variables de entorno"
echo "   - Railway creará automáticamente la base de datos"
echo ""
echo "3. 🌐 Desplegar frontend en Vercel:"
echo "   - Ve a https://vercel.com"
echo "   - Conecta tu repositorio de GitHub"
echo "   - Configura VITE_API_URL con la URL de Railway"
echo ""
echo "4. 🔧 Actualizar Azure App Registration:"
echo "   - Ve a https://portal.azure.com"
echo "   - Actualiza la URL de redirección con la URL de Railway"
echo ""
echo "📖 Para más detalles, consulta DEPLOYMENT.md"
echo ""
print_success "¡Script completado! Sigue los pasos manuales arriba."
