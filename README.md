# ElectBot – Election Process Education Assistant 🗳️

An **AI-powered, interactive** web application that educates citizens about the election process, timelines, voter registration, and democratic rights. Built with **Google Gemini AI** and **Google Maps** integration.

**Live Demo**: [Deployed on Google Cloud Run]

---

## 🎯 Chosen Vertical

**Election Process Education** – A smart assistant that helps users understand how elections work, from announcement to government formation, through an interactive and accessible interface.

---

## 🧠 Approach & Logic

### Architecture
- **Backend**: Python Flask with security middleware (Talisman, rate limiting, input sanitization)
- **AI Engine**: Google Gemini 2.0 Flash – provides contextual, non-partisan election education
- **Knowledge Base**: Structured JSON data covering 8 election phases, voter registration, voting methods, election types, and FAQs
- **Frontend**: Vanilla HTML/CSS/JS with glassmorphism design, smooth animations, and full accessibility

### Decision Logic
1. **User queries** are sanitized and sent to Google Gemini AI with election-specific system instructions
2. **Context injection**: The knowledge base is provided alongside user queries for accurate, grounded responses
3. **Fallback system**: If Gemini is unavailable, intelligent keyword-matching provides structured responses from the knowledge base
4. **Non-partisan**: The AI is instructed to remain neutral and redirect political opinion questions to factual information

### Smart Features
- **Conversational AI**: Context-aware chat with conversation history
- **Interactive Timeline**: 8-phase election process with expandable details
- **Knowledge Quiz**: 10-question assessment with explanations and scoring
- **Polling Location Finder**: Google Maps integration for finding nearby polling stations
- **Accessibility**: Skip navigation, ARIA labels, high contrast mode, adjustable font sizes, keyboard navigation

---

## 🔧 How the Solution Works

### Pages & Features
| Feature | Description |
|---------|-------------|
| **Home** | Hero section with animated cards, feature navigation, election statistics |
| **Timeline** | Interactive 8-phase election process with expandable details |
| **AI Chat** | Google Gemini-powered chatbot with quick questions sidebar |
| **Quiz** | 10-question assessment with progress tracking, explanations, and scoring |
| **Map** | Google Maps integration for polling station search |

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application page |
| `/api/chat` | POST | AI chat (Gemini + fallback) |
| `/api/knowledge/<category>` | GET | Structured election data |
| `/api/quiz` | GET | Quiz questions |
| `/api/health` | GET | Health check for Cloud Run |
| `/api/clear-history` | POST | Clear chat session |

### Tech Stack
- **Backend**: Flask, Gunicorn
- **AI**: Google Gemini 2.0 Flash (generative AI)
- **Maps**: Google Maps JavaScript API + Places Library
- **Security**: Flask-Talisman (CSP, HTTPS), Flask-Limiter (rate limiting), input sanitization
- **Testing**: Pytest with comprehensive coverage
- **Deployment**: Docker → Google Cloud Run

---

## 🚀 Deployment (Google Cloud Run)

### Prerequisites
- Google Cloud account with billing enabled
- `gcloud` CLI installed and authenticated
- Google Gemini API key from [AI Studio](https://aistudio.google.com/apikey)
- Google Maps API key from [Cloud Console](https://console.cloud.google.com/apis)

### Deploy Steps
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy electbot \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=your_key,GOOGLE_MAPS_API_KEY=your_maps_key"
```

### Local Development
```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key
export GOOGLE_MAPS_API_KEY=your_maps_key
python app.py
```

### Run Tests
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## ✅ Google Services Integration

| Service | Usage |
|---------|-------|
| **Google Gemini AI** | Powers the chatbot with contextual, non-partisan election education |
| **Google Maps API** | Polling station finder with Places search and geolocation |
| **Google Cloud Run** | Serverless deployment with auto-scaling |
| **Google Fonts** | Inter font family for premium typography |

---

## 📋 Assumptions

1. Primary focus is on the **Indian election system** (Election Commission of India) but the AI can answer about global elections
2. The AI assistant remains **strictly non-partisan** – no political opinions or party endorsements
3. Users should verify critical information (dates, eligibility) with official sources like [eci.gov.in](https://www.eci.gov.in)
4. Google Maps API key is optional – the app functions without it using a fallback UI
5. The knowledge base covers the most common election topics; edge cases are handled by Gemini AI

---

## 🔒 Security Measures

- **Content Security Policy** (CSP) via Flask-Talisman
- **Rate Limiting**: 30 requests/min for chat, 60/min for knowledge API
- **Input Sanitization**: HTML stripping, length limits (2000 chars)
- **Session Security**: Server-side session management
- **HTTPS**: Enforced in production via Cloud Run

---

## ♿ Accessibility

- **Skip Navigation** link for keyboard users
- **ARIA labels** on all interactive elements
- **Semantic HTML5** structure (`<header>`, `<main>`, `<nav>`, `<footer>`)
- **High Contrast Mode** toggle
- **Adjustable Font Size** (3 levels)
- **Keyboard Navigation** support for all features
- **Screen reader** friendly with role attributes and aria-live regions

---

## 📁 Project Structure

```
election/
├── app.py                 # Flask application + API + knowledge base
├── requirements.txt       # Python dependencies
├── Dockerfile             # Cloud Run deployment
├── .dockerignore          # Docker build exclusions
├── .gitignore             # Git exclusions
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css      # Design system + responsive styles
│   └── js/
│       └── app.js         # Frontend logic
├── tests/
│   └── test_app.py        # Comprehensive test suite
└── README.md              # This file
```

---

**Built with ❤️ for democratic education**
