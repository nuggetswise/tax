# 🚀 Quick Start Guide

Get the Agentic Tax Return Drafter running in 5 minutes!

## ⚡ Super Quick Setup

### 1. Clone & Setup
```bash
git clone <repository-url>
cd agentic-tax-drafter
chmod +x setup.sh
./setup.sh
```

### 2. Add Your OpenAI API Key
```bash
# Edit the .env file
nano .env

# Add your API key:
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Don't have an API key?** Get one at [OpenAI Platform](https://platform.openai.com/api-keys)

### 3. Run the App
```bash
poetry run streamlit run streamlit_app.py
```

### 4. Open Your Browser
Go to: http://localhost:8501

## 🧪 Test with Sample Data

1. **Upload the sample file**: `sample_data/client_gl_2024.csv`
2. **Click "Start Workflow"**
3. **Watch the AI agents work!**

## 📊 What You'll See

### Workflow Progress
- ✅ **ExtractData**: Processes your documents
- ✅ **DraftForms**: AI populates Form 1120
- ✅ **Diagnostics**: Finds potential issues
- ✅ **Adjustments**: Suggests improvements

### Results Tabs
- **📄 Form 1120**: Complete tax form with editable fields
- **📋 Schedules**: Schedule C and M-1
- **⚠️ Diagnostics**: Issues found by the system
- **🔧 Adjustments**: AI-suggested corrections
- **📈 Summary**: Key metrics and reasoning

## 🎯 Expected Results

With the sample data, you should see:
- **Gross Receipts**: $1,250,000
- **Cost of Goods Sold**: $875,000
- **High COGS Ratio Warning**: Flagged as unusually high
- **Adjustment Suggestion**: Reduce COGS to $750,000 (60% ratio)

## 🔧 Troubleshooting

### "OpenAI API key not found"
- Make sure you added your API key to the `.env` file
- Check that the key starts with `sk-`

### "Poetry not found"
- Run: `curl -sSL https://install.python-poetry.org | python3 -`
- Add to PATH: `export PATH="/Users/$USER/.local/bin:$PATH"`

### "Port already in use"
- Change port in `.env`: `STREAMLIT_SERVER_PORT=8502`
- Or kill existing process: `pkill -f streamlit`

## 🚀 Next Steps

- Upload your own tax documents
- Try different file formats (PDF, Excel)
- Explore the provenance trail in the sidebar
- Apply AI suggestions and see real-time updates

**Happy tax drafting! 🎉** 