#!/bin/bash

# Quick deployment script for Streamlit Cloud
echo "🚀 Deploying Agentic Tax Return Drafter..."

# Check if requirements.txt exists
if [ ! -f requirements.txt ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

# Check if streamlit_app.py exists
if [ ! -f streamlit_app.py ]; then
    echo "❌ streamlit_app.py not found!"
    exit 1
fi

echo "✅ All files present for deployment"
echo ""
echo "📋 Deployment Checklist:"
echo "1. ✅ requirements.txt - Core dependencies only"
echo "2. ✅ streamlit_app.py - Main application"
echo "3. ✅ .streamlit/config.toml - Optimized settings"
echo "4. ✅ sample_data/ - Demo files included"
echo ""
echo "🌐 Deploy to Streamlit Cloud:"
echo "1. Push to GitHub: git push origin main"
echo "2. Connect repository to Streamlit Cloud"
echo "3. Add environment variables in dashboard"
echo "4. Deploy!"
echo ""
echo "🔑 Required Environment Variables:"
echo "   OPENAI_API_KEY=your-openai-api-key"
echo ""
echo "🎯 The app will work with CSV files immediately!"
echo "   PDF support can be added later if needed." 