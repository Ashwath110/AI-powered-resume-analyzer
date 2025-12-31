# AI-Powered Resume Analyzer

An intelligent resume analysis tool that checks for AI-generated content, validates resume length, and provides ATS scoring with detailed recommendations.

## Features

🤖 **AI Content Detection** - Identifies AI-generated resumes
📏 **Length Validation** - Enforces one-page resume standard
📊 **ATS Scoring** - Industry-standard evaluation
🎯 **Skill Gap Analysis** - Visual comparisons
📁 **File Upload** - Support for PDF, DOCX, TXT
💡 **Smart Recommendations** - Actionable improvements

## Live Demo

🌐 **[Try it now!](#)** _(Link will be available after deployment)_

## Quick Start

1. Upload or paste your resume
2. Upload or paste job description
3. Click "Analyze Resume"
4. Get instant feedback with detailed metrics

## Technology Stack

- **Frontend:** Streamlit
- **ML Models:** Sentence Transformers (MPNet-v2)
- **AI Detection:** Custom NLP algorithms
- **Visualizations:** Plotly
- **PDF Processing:** PyPDF2, pdfplumber

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Validation Criteria

✅ **Resume Length:** Max 600 words, 3,500 characters (1 page)
✅ **AI Detection:** Multi-signal analysis with confidence scoring
✅ **ATS Score:** 5-dimensional evaluation (Skill Match, Semantic Match, Completeness, Balance, Formatting)

## Rejection Criteria

❌ Resume exceeds 1 page (>600 words or >3,500 characters)
❌ AI-generated content detected (>60% AI probability)

## License

MIT License

## Author

Built with ❤️ using Python, Streamlit, and AI
