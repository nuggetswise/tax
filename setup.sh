#!/bin/bash

# Agentic Tax Return Drafter Setup Script

echo "🚀 Setting up Agentic Tax Return Drafter..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file and add your OpenAI API key!"
    echo "   OPENAI_API_KEY=your-actual-api-key-here"
else
    echo "✅ .env file already exists"
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "📦 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    echo "📝 Add Poetry to your PATH: export PATH=\"/Users/\$USER/.local/bin:\$PATH\""
else
    echo "✅ Poetry is already installed"
fi

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. Run: poetry run streamlit run streamlit_app.py"
echo "3. Open: http://localhost:8501"
echo ""
echo "📁 Sample data available in: sample_data/client_gl_2024.csv" 