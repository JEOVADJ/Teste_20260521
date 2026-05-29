#!/bin/bash
# Script de inicialização do projeto IoT Dashboard

echo "=========================================="
echo "  IoT Dashboard - Sistema de Inicialização"
echo "=========================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não está instalado"
    exit 1
fi
echo "✅ Python 3 encontrado: $(python3 --version)"

# Criar ambiente virtual (opcional)
if [ ! -d "backend/venv" ]; then
    echo ""
    echo "🔧 Criando ambiente virtual..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    cd ..
fi

# Ativar ambiente virtual
source backend/venv/bin/activate

# Instalar dependências
echo ""
echo "📦 Instalando dependências..."
pip install -r backend/requirements.txt -q

# Verificar .env
echo ""
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Arquivo .env não encontrado"
    echo "📋 Criando .env a partir de .env.example..."
    cp backend/.env.example backend/.env
    echo "✅ .env criado. Configure suas variáveis:"
    echo "   - MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD"
    echo "   - MQTT_BROKER"
    echo ""
    read -p "Deseja continuar mesmo assim? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "✅ Tudo pronto!"
echo ""
echo "Para iniciar o servidor:"
echo "  cd backend"
echo "  python app.py"
echo ""
echo "Acesse: http://localhost:5000"
