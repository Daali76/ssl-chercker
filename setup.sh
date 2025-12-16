#!/bin/bash
# Quick Setup and Run Script for SSL Checker

set -e

echo "🚀 SSL Checker - Quick Setup"
echo "=============================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env created. Please update it with your settings."
fi

# Check if venv exists, if not create it
if [ ! -d venv ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install/upgrade requirements
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Test imports
echo "🧪 Testing imports..."
python3 -c "from app.core.config import settings; print('✅ Config loaded')"
python3 -c "import main; print('✅ App loaded')"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Now you can run the app in two ways:"
echo ""
echo "1️⃣  Local development:"
echo "   python main.py"
echo ""
echo "2️⃣  Docker deployment:"
echo "   docker-compose up -d"
echo ""
echo "📖 Access the app at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
echo ""
