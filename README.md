# ElectBot 🗳️ – Premium AI Election Heritage Assistant

[![Deploy to Cloud Run](https://img.shields.io/badge/Deploy-Cloud_Run-4285F4?logo=google-cloud&logoColor=white)](https://electbot.run.app)
[![Powered by Gemini](https://img.shields.io/badge/AI-Gemini_2.0_Flash-6366f1?logo=google-gemini&logoColor=white)](https://aistudio.google.com)
[![Modern UI](https://img.shields.io/badge/Design-Glassmorphism-FF4081?logo=css3&logoColor=white)](https://github.com/Aayush9-spec/ElectBot)

**ElectBot** is a professional-grade, interactive educational platform designed to empower citizens with high-fidelity knowledge of the electoral process. Leveraging **Google Gemini 2.0 Flash**, **Google Maps**, and **Google Calendar**, it provides a seamless, premium experience for mastering democratic procedures.

---

## 🎯 Project Vertical: Election Education & Civic Engagement
*A smart, dynamic assistant that transforms complex electoral bureaucracy into an intuitive, visually stunning roadmap.*

---

## 🚀 Key Innovation & Google Services
This project goes beyond a simple chatbot, integrating deep Google ecosystem services to solve real-world educational challenges:

| Service | Implementation | Purpose |
|---------|----------------|---------|
| **Google Gemini 2.0 Flash** | Context-grounded AI Assistant | Delivers accurate, non-partisan, and structured guidance on complex registration and voting procedures. |
| **Google Maps (Places/Maps/JS)** | Interactive Booth Locator | Real-time discovery of polling stations and registration centers with precision geolocation. |
| **Google Calendar** | Event Integration | One-click synchronization of election notification phases directly to the user's personal calendar. |
| **Google Analytics 4** | Advanced Telemetry | Data-driven insights into user engagement and common civic knowledge gaps. |
| **Google Cloud Run** | Scalable Infrastructure | Enterprise-grade serverless hosting with auto-scaling and high availability. |

---

## 🧠 Approach & Decision Logic

### 1. The Heritage Design System
We implemented a custom-built **Glassmorphism Design System** that balances premium aesthetics with high performance.
- **Visuals**: Dark-themed translucent surfaces, vibrant gradients (`indigo`, `rose`, `amber`), and animated background orbs.
- **Responsiveness**: Fluid grid layouts that adapt from mobile viewports to ultra-wide displays.
- **Performance**: Optimized asset delivery, minified code, and Gzip compression.

### 2. Grounded AI Logic
- **Knowledge Injection**: Before querying Gemini, the system injects structured ECI knowledge (Gazette rules, MCC codes, voting tech) to ensure the AI doesn't hallucinate.
- **Non-Partisan Enforcement**: A strict system-level prompt ensures ElectBot remains a neutral educator, redirecting political debates to constitutional facts.
- **State Management**: Session-based conversation history allows for multi-turn dialogues on complex topics like "VVPAT verification."

### 3. Civic Mastery Path
- **Interactive Roadmap**: A visual 8-phase timeline that breaks down the election cycle.
- **Adaptive Quiz**: A 10-level assessment that benchmark's user knowledge with instant feedback and certification metrics.

---

## 🔒 Security & Reliability
- **Content Security Policy (CSP)**: Hardened headers via `Flask-Talisman` to prevent XSS and data injection.
- **Rate Limiting**: `Flask-Limiter` protects AI resources from abuse.
- **Privacy First**: No personal data collection; analytics are anonymized via GA4.
- **Health Monitoring**: Integrated `/api/health` endpoints for Cloud Run stability.

---

## 🔧 Technical Setup

### Local Development
```bash
# 1. Clone & Install
git clone https://github.com/Aayush9-spec/ElectBot
pip install -r requirements.txt

# 2. Configure Environment
export GEMINI_API_KEY="your_key"
export GOOGLE_MAPS_API_KEY="your_key"

# 3. Launch
python app.py
```

### Production Deployment (GCP)
```bash
gcloud run deploy electbot --source . --region asia-south1 \
  --set-env-vars "GEMINI_API_KEY=xxx,GOOGLE_MAPS_API_KEY=yyy"
```

---

## ♿ Inclusive Design
- **High Contrast Mode**: Tailored for users with visual impairments.
- **Dynamic Scaling**: Adjustable typography for better readability.
- **ARIA/Semantic HTML**: Fully accessible to screen readers.
- **Keyboard Optimized**: 100% functionality without a mouse.

---

### 📁 Architecture
- `app.py`: Hardened Flask Engine (Security, AI, API, Config)
- `election_knowledge.json`: Externalized Knowledge Base (SSOT)
- `static/css/style.css`: Custom Glassmorphism Design System
- `static/js/app.js`: Interactive Logic & Maps Integration
- `tests/`: Automated validation suite
    - `test_app.py`: API & Functional Tests
    - `test_security.py`: Header & CSP Validation
    - `test_performance.py`: Latency Benchmarking

---

## 🧪 Validation & Quality Assurance
We achieved a high-reliability score through a multi-layered testing strategy:
- **Functional Testing**: Validating all API endpoints (Chat, Quiz, Health).
- **Security Auditing**: Automated checks for Talisman security headers and Content Security Policy.
- **Performance Benchmarking**: Ensuring `<500ms` page loads and `<100ms` API latencies.
- **Code Coverage**: Maintaining comprehensive coverage across core logic in `app.py`.

Run tests:
```bash
export PYTHONPATH=.
pytest --cov=app tests/
```

---
**Built with ❤️ by the ElectBot Team to strengthen Democracy.**
