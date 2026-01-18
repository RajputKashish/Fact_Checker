# Fact Checker - Assignment Presentation Script

## 🎤 2-Minute Pitch Script

---

### Opening (15 seconds)
"Hi, I built a **Fact-Checking Web App** that can automatically verify claims in PDF documents against live web data. Let me show you how it works."

---

### The Problem (15 seconds)
"We all know misinformation is everywhere. Documents contain outdated statistics, wrong numbers, and sometimes outright false claims. Manually fact-checking is time-consuming and error-prone."

---

### My Solution (30 seconds)
"My app solves this in three steps:

1. **Upload** any PDF document
2. The AI **extracts** all verifiable claims - statistics, dates, financial figures
3. It **searches the web** and flags each claim as:
   - ✅ Verified
   - ⚠️ Inaccurate (outdated data)
   - ❌ False

For example, if you upload a 2019 IMF report with old GDP figures, my app will flag them as inaccurate and show you the current numbers."

---

### Tech Stack (20 seconds)
"Here's what powers it:
- **Streamlit** for the web interface
- **Groq's Llama 3.1** for AI analysis (it's free!)
- **Tavily** for real-time web search
- **PyMuPDF** for PDF processing

The best part? Both APIs I used have free tiers, so this costs nothing to run."

---

### Demo Highlights (30 seconds)
"Let me show you a quick demo:
1. I upload this IMF 2019 economic report
2. The app extracts 10+ claims about GDP, growth rates, etc.
3. It verifies each one against current data
4. Look - it correctly flags these 2019 figures as 'Inaccurate' and shows the updated 2024 numbers"

---

### Closing (10 seconds)
"The app is deployed and live. You can try it right now at [your-app-url]. Any questions?"

---

## 📋 Key Points to Emphasize

1. **Automated Claim Extraction** - AI identifies what needs to be verified
2. **Live Web Data** - Always checks against current information
3. **Clear Verdicts** - Three categories: Verified, Inaccurate, False
4. **Source Citations** - Every verdict comes with sources
5. **Free to Run** - Uses Groq (free) + Tavily (free tier)

## 🎯 Evaluation Criteria Addressed

| Criteria | How I Addressed It |
|----------|-------------------|
| Extract claims | AI extracts statistics, dates, financial figures, technical specs |
| Verify against web | Tavily API searches live web data |
| Flag accuracy | Three-tier system: Verified / Inaccurate / False |
| Deployed & accessible | Streamlit Cloud deployment with live URL |
| Clean code | Modular architecture with separate extractors and verifiers |

## 💡 If Asked About Challenges

"The main challenge was choosing the right LLM. OpenAI was too expensive for this demo, so I switched to Groq which offers Llama 3.1 for free. The results are comparable, and it made the project cost-effective."

---

Good luck with your presentation! 🚀
