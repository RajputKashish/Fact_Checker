# 🔍 Fact Checker

An AI-powered fact-checking web app that extracts claims from PDFs and verifies them against live web data.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Groq](https://img.shields.io/badge/Groq-Llama_3.1-orange.svg)

## 🎯 What It Does

1. **Extract** - Upload a PDF and the app identifies specific claims (statistics, dates, financial figures, technical specs)
2. **Verify** - Each claim is searched against live web data using Tavily
3. **Report** - Claims are flagged as:
   - ✅ **Verified** - Matches current, reliable data
   - ⚠️ **Inaccurate** - Contains outdated or slightly wrong information
   - ❌ **False** - No evidence found or contradicted by sources

## 🚀 Live Demo

**[Try the App](https://fact-checker-app.streamlit.app)** ← Click to access the deployed application

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| LLM | Groq (Llama 3.1 8B) - **FREE** |
| Web Search | Tavily API |
| PDF Processing | PyMuPDF |
| Deployment | Streamlit Cloud |

## 📁 Project Structure

```
Fact Checker/
├── app.py                 # Main Streamlit application
├── src/
│   ├── models.py          # Data models (Claim, VerificationResult)
│   ├── pdf_extractor.py   # PDF text extraction
│   ├── claim_extractor.py # LLM-based claim identification
│   └── verifier.py        # Web search & verification logic
├── requirements.txt       # Dependencies
└── README.md
```

## 🔧 Local Setup

### Prerequisites
- Python 3.9+
- Groq API key (FREE at [console.groq.com](https://console.groq.com))
- Tavily API key (FREE at [tavily.com](https://tavily.com))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fact-checker.git
cd fact-checker

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_key" > .env
echo "TAVILY_API_KEY=your_tavily_key" >> .env

# Run the app
streamlit run app.py
```

## 📖 How It Works

```
PDF Upload → Text Extraction → Claim Identification → Web Search → Verification → Results
     │              │                  │                  │            │
     └──────────────┴──────────────────┴──────────────────┴────────────┘
                         Powered by Groq LLM + Tavily Search
```

1. **PDF Processing**: PyMuPDF extracts text from uploaded documents
2. **Claim Extraction**: Groq's Llama 3.1 identifies verifiable claims (numbers, dates, facts)
3. **Web Search**: Tavily searches for current information about each claim
4. **Verification**: LLM compares claims against search results
5. **Results**: Claims are classified and displayed with sources

## 🔑 API Keys

| API | Purpose | Get Key |
|-----|---------|---------|
| Groq | LLM for claim extraction & verification | [console.groq.com](https://console.groq.com) (FREE) |
| Tavily | Web search for fact-checking | [tavily.com](https://tavily.com) (FREE tier) |

## 🧪 Testing

Test with these sample PDFs:
- **WHO Constitution** - Contains verified historical facts
- **IMF WEO 2019** - Contains outdated economic data (should flag as Inaccurate)

## 📝 License

MIT License