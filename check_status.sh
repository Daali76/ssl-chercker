#!/bin/bash
# Quick Status Check for SSL Checker

echo "🔍 SSL Checker Status Check"
echo "=============================="
echo ""

# Check Python version
echo "📦 Python Version:"
python3 --version

# Check if venv exists
if [ -d venv ]; then
    echo "✅ Virtual environment found"
else
    echo "⚠️  Virtual environment not found - run: python3 -m venv venv"
fi

# Check requirements
echo ""
echo "📋 Dependencies:"
if command -v pip &> /dev/null; then
    if python3 -c "from dotenv import load_dotenv; from fastapi import FastAPI; from sqlalchemy import create_engine" 2>/dev/null; then
        echo "✅ Core dependencies installed"
    else
        echo "⚠️  Some dependencies missing - run: pip install -r requirements.txt"
    fi
else
    echo "⚠️  pip not found"
fi

# Check imports
echo ""
echo "🧪 Import Tests:"
python3 -c "from app.core.config import settings; print('✅ Config loads')" 2>/dev/null || echo "❌ Config import failed"
python3 -c "import main; print('✅ App loads')" 2>/dev/null || echo "❌ App import failed"

# Check env file
echo ""
echo "⚙️  Configuration:"
if [ -f .env ]; then
    echo "✅ .env file exists"
    if [ -f .env.example ]; then
        echo "✅ .env.example file exists"
    fi
else
    echo "⚠️  .env file not found - run: cp .env.example .env"
fi

echo ""
echo "=============================="
echo "✅ Status check complete!"
