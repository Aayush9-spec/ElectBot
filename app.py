"""
Election Process Education Assistant
A smart, interactive platform helping users understand the election process,
timelines, and steps using Google Gemini AI and Google Maps.

Author: Election Education Team
License: MIT
"""

import os
import json
import logging
import re
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify,
    session, send_from_directory
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_compress import Compress
import google.generativeai as genai

# ─── Configuration ───────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32).hex())

# Security headers via Talisman
csp = {
    'default-src': ["'self'"],
    'script-src': [
        "'self'",
        "https://maps.googleapis.com",
        "https://maps.gstatic.com",
        "https://cdn.jsdelivr.net"
    ],
    'style-src': [
        "'self'",
        "'unsafe-inline'",
        "https://fonts.googleapis.com",
        "https://cdn.jsdelivr.net"
    ],
    'font-src': [
        "'self'",
        "https://fonts.gstatic.com",
        "https://cdn.jsdelivr.net"
    ],
    'img-src': ["'self'", "data:", "https:", "blob:"],
    'connect-src': [
        "'self'",
        "https://generativelanguage.googleapis.com",
        "https://maps.googleapis.com"
    ],
    'frame-src': ["https://www.google.com", "https://maps.google.com"],
}

talisman = Talisman(
    app,
    content_security_policy=csp,
    force_https=False  # Cloud Run handles HTTPS termination
)

# Compression for performance
Compress(app)

# Rate limiting for security
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ─── Google Gemini AI Setup ──────────────────────────────────────────────────

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction="""You are 'ElectBot' – a friendly, knowledgeable, and non-partisan 
Election Process Education Assistant. Your mission is to help citizens understand how elections 
work in India and around the world.

CORE RESPONSIBILITIES:
1. Explain election processes step-by-step (voter registration, campaigning, polling, counting)
2. Clarify election timelines and important dates
3. Describe the roles of election bodies (e.g., Election Commission of India)
4. Explain voting methods (EVM, VVPAT, postal ballots, etc.)
5. Educate about voter rights and responsibilities
6. Describe the complete electoral cycle from announcement to results
7. Help users find their polling booths and check voter registration status
8. Explain different types of elections (General, State, Local Body, By-elections)

RULES:
- Always remain NEUTRAL and NON-PARTISAN – never favor any political party
- Provide FACTUAL information backed by official sources
- If asked about political opinions, politely redirect to factual election process information
- Use simple, easy-to-understand language
- When appropriate, suggest official resources like https://www.eci.gov.in
- Format responses with clear headings, bullet points, and numbered steps when helpful
- Use emojis sparingly for friendliness (🗳️ ✅ 📋 🏛️)
- Always encourage democratic participation
- If unsure about specific dates or local regulations, advise checking official sources
- Support accessibility – be clear and structured in responses

RESPONSE FORMAT:
- Use markdown formatting for better readability
- Keep responses concise but comprehensive
- Break complex processes into numbered steps
- Include relevant timelines when discussing election schedules
- End with a helpful suggestion or related topic the user might want to explore"""
    )
    logger.info("✅ Google Gemini AI initialized successfully")
else:
    model = None
    logger.warning("⚠️ GEMINI_API_KEY not set – AI features will use fallback responses")


# ─── Election Knowledge Base ────────────────────────────────────────────────

ELECTION_KNOWLEDGE = {
    "timeline": {
        "title": "Election Timeline & Key Phases",
        "icon": "📅",
        "phases": [
            {
                "name": "Announcement & Notification",
                "duration": "6-8 weeks before polling",
                "description": "Election Commission announces election dates, issues notification, and the Model Code of Conduct comes into effect.",
                "details": [
                    "Election Commission issues press conference",
                    "Gazette notification published",
                    "Model Code of Conduct enforced immediately",
                    "Political parties begin preparations"
                ]
            },
            {
                "name": "Nomination Filing",
                "duration": "7 days from notification",
                "description": "Candidates file their nomination papers along with required documents and security deposit.",
                "details": [
                    "Candidates collect nomination forms",
                    "Security deposit: ₹25,000 (General), ₹12,500 (SC/ST)",
                    "Affidavit with criminal, financial, educational details",
                    "Filing before Returning Officer"
                ]
            },
            {
                "name": "Scrutiny of Nominations",
                "duration": "1 day after last date of filing",
                "description": "Returning Officer examines all nomination papers for validity and completeness.",
                "details": [
                    "Verification of documents",
                    "Check eligibility criteria",
                    "Objections can be raised by other candidates",
                    "Invalid nominations rejected with reasons"
                ]
            },
            {
                "name": "Withdrawal of Candidature",
                "duration": "2 days after scrutiny",
                "description": "Candidates may choose to withdraw their nomination before the deadline.",
                "details": [
                    "Written notice to Returning Officer",
                    "Cannot be reversed after submission",
                    "Final list of candidates prepared",
                    "Allotment of election symbols"
                ]
            },
            {
                "name": "Election Campaign",
                "duration": "Until 48 hours before polling",
                "description": "Political parties and candidates campaign to reach voters through rallies, advertisements, and door-to-door canvassing.",
                "details": [
                    "Rallies, roadshows, and public meetings",
                    "TV, radio, print, and social media campaigns",
                    "Campaign expenditure limits enforced",
                    "Campaign silence period: 48 hours before voting"
                ]
            },
            {
                "name": "Polling Day",
                "duration": "1 day (7 AM - 6 PM typically)",
                "description": "Voters cast their votes at designated polling stations using Electronic Voting Machines (EVMs).",
                "details": [
                    "Voter identity verification at booth",
                    "Indelible ink applied on left index finger",
                    "EVM and VVPAT based voting",
                    "Special provisions for disabled and elderly voters"
                ]
            },
            {
                "name": "Counting & Results",
                "duration": "Usually 2-3 days after polling",
                "description": "Votes are counted at designated counting centers under strict supervision.",
                "details": [
                    "Postal ballots counted first",
                    "EVM counting round by round",
                    "VVPAT verification of random machines",
                    "Results declared by Returning Officer"
                ]
            },
            {
                "name": "Government Formation",
                "duration": "Within days of results",
                "description": "Winning party/coalition is invited to form the government and take oath of office.",
                "details": [
                    "Governor/President invites majority party",
                    "Leader elected as PM/CM",
                    "Cabinet ministers appointed",
                    "Government sworn in and begins functioning"
                ]
            }
        ]
    },
    "voter_registration": {
        "title": "How to Register as a Voter",
        "icon": "📋",
        "steps": [
            {"step": 1, "title": "Check Eligibility", "description": "Must be an Indian citizen, 18+ years old, and a resident of the constituency"},
            {"step": 2, "title": "Gather Documents", "description": "Aadhaar card, passport, driving license, or other valid ID proof; address proof; passport-size photos"},
            {"step": 3, "title": "Fill Form 6", "description": "Available online at nvsp.in or at the local Electoral Registration Office"},
            {"step": 4, "title": "Submit Application", "description": "Submit online through NVSP portal or offline at ERO office with documents"},
            {"step": 5, "title": "Verification", "description": "Booth Level Officer (BLO) visits for physical verification"},
            {"step": 6, "title": "Receive EPIC", "description": "Elector's Photo Identity Card (Voter ID) issued after approval"}
        ]
    },
    "voting_methods": {
        "title": "Voting Methods in India",
        "icon": "🗳️",
        "methods": [
            {
                "name": "Electronic Voting Machine (EVM)",
                "description": "Standalone electronic device used at polling stations. Contains Ballot Unit (BU), Control Unit (CU).",
                "security": "Tamper-proof, one-time programmable chip, no network connectivity"
            },
            {
                "name": "VVPAT (Voter Verifiable Paper Audit Trail)",
                "description": "Attached to EVM, prints a slip showing candidate name and symbol for 7 seconds before it drops into a sealed box.",
                "security": "Provides paper trail for verification, used in random audits"
            },
            {
                "name": "Postal Ballot",
                "description": "Available for service voters (military, diplomats), special voters, election duty staff, and voters above 80 years.",
                "security": "Sealed envelope system, verified at counting center"
            },
            {
                "name": "Braille Ballot",
                "description": "Special provision for visually impaired voters with Braille-enabled EVMs.",
                "security": "Ensures accessibility and independent voting"
            }
        ]
    },
    "election_types": {
        "title": "Types of Elections in India",
        "icon": "🏛️",
        "types": [
            {"name": "General Elections (Lok Sabha)", "frequency": "Every 5 years", "scope": "Nationwide – 543 constituencies", "authority": "Election Commission of India"},
            {"name": "State Assembly Elections (Vidhan Sabha)", "frequency": "Every 5 years", "scope": "State-level constituencies", "authority": "Election Commission of India"},
            {"name": "Local Body Elections (Panchayat/Municipal)", "frequency": "Every 5 years", "scope": "District/City level", "authority": "State Election Commission"},
            {"name": "Rajya Sabha Elections", "frequency": "Biennial (1/3 members every 2 years)", "scope": "State legislatures elect members", "authority": "Election Commission of India"},
            {"name": "By-Elections", "frequency": "As needed", "scope": "Specific vacant constituencies", "authority": "Election Commission of India"},
            {"name": "Presidential Election", "frequency": "Every 5 years", "scope": "Electoral college of MPs and MLAs", "authority": "Election Commission of India"}
        ]
    },
    "voter_rights": {
        "title": "Voter Rights & Responsibilities",
        "icon": "⚖️",
        "rights": [
            "Right to vote without discrimination (Article 326)",
            "Right to secret ballot",
            "Right to information about candidates (affidavits)",
            "Right to NOTA (None of the Above) option",
            "Right to assisted voting (for disabled voters)",
            "Right to paid leave on polling day",
            "Right to lodge complaints about electoral malpractice",
            "Right to challenge election results through election petition"
        ],
        "responsibilities": [
            "Register as a voter when eligible",
            "Verify your name in the electoral roll before elections",
            "Carry valid voter ID to the polling station",
            "Vote independently without being influenced",
            "Maintain discipline at the polling station",
            "Report any electoral malpractice",
            "Respect the democratic process and its outcomes",
            "Stay informed about candidates and their manifestos"
        ]
    },
    "faqs": [
        {"q": "What is the minimum age to vote?", "a": "18 years as on the qualifying date (January 1st of the year of electoral roll revision)."},
        {"q": "Can NRIs vote?", "a": "Yes, NRIs can register as overseas voters and vote in person at their registered constituency."},
        {"q": "What is NOTA?", "a": "NOTA (None of the Above) allows voters to reject all candidates. It was introduced by the Supreme Court in 2013."},
        {"q": "What is the Model Code of Conduct?", "a": "A set of guidelines for political parties and candidates to ensure free and fair elections, enforced from announcement to results."},
        {"q": "How is EVM tampering prevented?", "a": "EVMs use one-time programmable chips, have no wireless connectivity, undergo mock polls, and are sealed in the presence of candidates' agents."},
        {"q": "What is the VVPAT?", "a": "Voter Verifiable Paper Audit Trail – a machine attached to the EVM that prints a paper slip showing the candidate voted for, visible for 7 seconds."},
        {"q": "Can I vote if I lost my Voter ID?", "a": "Yes, you can use 12 alternative ID documents (Aadhaar, Passport, DL, PAN card, etc.) as listed by ECI."},
        {"q": "What happens if there's a tie?", "a": "In case of a tie, the Returning Officer decides the winner by drawing lots, as per the Representation of the People Act."}
    ]
}


# ─── Helper Functions ────────────────────────────────────────────────────────

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text or not isinstance(text, str):
        return ""
    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    # Limit length
    clean = clean[:2000]
    return clean.strip()


def get_fallback_response(query: str) -> str:
    """Provide intelligent fallback responses when Gemini is unavailable."""
    query_lower = query.lower()

    if any(word in query_lower for word in ["register", "registration", "enroll", "sign up"]):
        data = ELECTION_KNOWLEDGE["voter_registration"]
        steps = "\n".join([f"**Step {s['step']}**: {s['title']} – {s['description']}" for s in data["steps"]])
        return f"## 📋 {data['title']}\n\n{steps}\n\n🔗 Visit [NVSP Portal](https://www.nvsp.in) for online registration."

    if any(word in query_lower for word in ["timeline", "schedule", "dates", "when", "phase"]):
        data = ELECTION_KNOWLEDGE["timeline"]
        phases = "\n".join([f"**{i+1}. {p['name']}** ({p['duration']}): {p['description']}" for i, p in enumerate(data["phases"])])
        return f"## 📅 {data['title']}\n\n{phases}"

    if any(word in query_lower for word in ["evm", "voting machine", "vvpat", "postal", "ballot"]):
        data = ELECTION_KNOWLEDGE["voting_methods"]
        methods = "\n".join([f"### {m['name']}\n{m['description']}\n🔒 **Security**: {m['security']}" for m in data["methods"]])
        return f"## 🗳️ {data['title']}\n\n{methods}"

    if any(word in query_lower for word in ["type", "kinds", "lok sabha", "rajya", "panchayat", "municipal"]):
        data = ELECTION_KNOWLEDGE["election_types"]
        types = "\n".join([f"- **{t['name']}**: {t['frequency']} | {t['scope']}" for t in data["types"]])
        return f"## 🏛️ {data['title']}\n\n{types}"

    if any(word in query_lower for word in ["right", "responsibility", "duty", "nota"]):
        data = ELECTION_KNOWLEDGE["voter_rights"]
        rights = "\n".join([f"✅ {r}" for r in data["rights"]])
        responsibilities = "\n".join([f"📌 {r}" for r in data["responsibilities"]])
        return f"## ⚖️ {data['title']}\n\n### Your Rights\n{rights}\n\n### Your Responsibilities\n{responsibilities}"

    # Check FAQs
    for faq in ELECTION_KNOWLEDGE["faqs"]:
        if any(word in query_lower for word in faq["q"].lower().split()[:3]):
            return f"**Q: {faq['q']}**\n\n{faq['a']}"

    return (
        "## 🗳️ Welcome to ElectBot!\n\n"
        "I can help you understand the election process. Try asking about:\n\n"
        "- 📅 **Election Timeline** – phases from announcement to results\n"
        "- 📋 **Voter Registration** – how to register as a voter\n"
        "- 🗳️ **Voting Methods** – EVMs, VVPAT, postal ballots\n"
        "- 🏛️ **Types of Elections** – Lok Sabha, State, Local body\n"
        "- ⚖️ **Voter Rights** – your rights and responsibilities\n"
        "- 📍 **Polling Locations** – find your nearest booth\n\n"
        "Just type your question and I'll guide you through!"
    )


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main application page."""
    return render_template(
        "index.html",
        maps_api_key=MAPS_API_KEY,
        current_year=datetime.now().year
    )


@app.route("/api/chat", methods=["POST"])
@limiter.limit("30 per minute")
def chat():
    """Handle AI chat requests using Google Gemini."""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Message is required"}), 400

        user_message = sanitize_input(data["message"])
        if not user_message:
            return jsonify({"error": "Invalid message"}), 400

        # Get conversation history from session
        if "history" not in session:
            session["history"] = []

        # Try Gemini AI first
        if model:
            try:
                # Build context with knowledge base
                context = f"""
User Question: {user_message}

Reference Knowledge Base (use this for accurate responses):
{json.dumps(ELECTION_KNOWLEDGE, indent=2)[:4000]}
"""
                chat_session = model.start_chat(history=[
                    {"role": h["role"], "parts": [h["content"]]}
                    for h in session["history"][-10:]  # Last 10 messages for context
                ])

                response = chat_session.send_message(context)
                ai_response = response.text

                # Update session history
                session["history"].append({"role": "user", "content": user_message})
                session["history"].append({"role": "model", "content": ai_response})
                session.modified = True

                logger.info(f"Gemini response generated for: {user_message[:50]}...")
                return jsonify({
                    "response": ai_response,
                    "source": "gemini",
                    "timestamp": datetime.now().isoformat()
                })

            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                # Fall through to fallback

        # Fallback response
        fallback = get_fallback_response(user_message)
        return jsonify({
            "response": fallback,
            "source": "knowledge_base",
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route("/api/knowledge/<category>")
@limiter.limit("60 per minute")
def get_knowledge(category):
    """Retrieve structured election knowledge by category."""
    if category not in ELECTION_KNOWLEDGE:
        return jsonify({"error": "Category not found"}), 404

    return jsonify({
        "data": ELECTION_KNOWLEDGE[category],
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/quiz", methods=["GET"])
@limiter.limit("20 per minute")
def get_quiz():
    """Return election knowledge quiz questions."""
    quiz_questions = [
        {
            "id": 1,
            "question": "What is the minimum age to vote in Indian elections?",
            "options": ["16 years", "18 years", "21 years", "25 years"],
            "correct": 1,
            "explanation": "As per Article 326 of the Indian Constitution, every citizen who is 18 years or above is eligible to vote."
        },
        {
            "id": 2,
            "question": "What does EVM stand for?",
            "options": ["Electronic Vote Machine", "Electronic Voting Machine", "Election Voting Method", "Electronic Verification Machine"],
            "correct": 1,
            "explanation": "EVM stands for Electronic Voting Machine, used in Indian elections since 2004 nationwide."
        },
        {
            "id": 3,
            "question": "When does the Model Code of Conduct come into effect?",
            "options": ["On polling day", "When results are announced", "When elections are announced", "One week before polling"],
            "correct": 2,
            "explanation": "The Model Code of Conduct comes into force immediately when the Election Commission announces the election schedule."
        },
        {
            "id": 4,
            "question": "What is NOTA?",
            "options": ["A political party", "None of the Above option", "A voting machine type", "A type of ballot paper"],
            "correct": 1,
            "explanation": "NOTA (None of the Above) was introduced by the Supreme Court in 2013, allowing voters to reject all candidates."
        },
        {
            "id": 5,
            "question": "How many constituencies are there in the Lok Sabha?",
            "options": ["500", "543", "550", "600"],
            "correct": 1,
            "explanation": "The Lok Sabha has 543 elected constituencies across India, plus 2 nominated Anglo-Indian members (until 2020)."
        },
        {
            "id": 6,
            "question": "What is VVPAT used for?",
            "options": ["Counting votes", "Verifying the vote cast on EVM", "Registering voters", "Identifying polling stations"],
            "correct": 1,
            "explanation": "VVPAT (Voter Verifiable Paper Audit Trail) prints a paper slip showing the candidate voted for, providing a verification mechanism."
        },
        {
            "id": 7,
            "question": "Which body conducts elections in India?",
            "options": ["Supreme Court", "Parliament", "Election Commission of India", "President of India"],
            "correct": 2,
            "explanation": "The Election Commission of India (ECI), established in 1950, is an autonomous constitutional body responsible for conducting elections."
        },
        {
            "id": 8,
            "question": "What is the campaign silence period before polling?",
            "options": ["12 hours", "24 hours", "48 hours", "72 hours"],
            "correct": 2,
            "explanation": "Campaigning must stop 48 hours before polling day to allow voters to make decisions without last-minute influence."
        },
        {
            "id": 9,
            "question": "What form is used for voter registration?",
            "options": ["Form 1", "Form 6", "Form 10", "Form 49A"],
            "correct": 1,
            "explanation": "Form 6 is used for new voter registration. It can be submitted online via the NVSP portal or at the local ERO office."
        },
        {
            "id": 10,
            "question": "What color ink is used to mark voters on polling day?",
            "options": ["Blue", "Red", "Indelible purple/black", "Green"],
            "correct": 2,
            "explanation": "Indelible ink (usually purple/black) is applied to the left index finger to prevent duplicate voting. It lasts for several weeks."
        }
    ]
    return jsonify({"questions": quiz_questions})


@app.route("/api/health")
def health_check():
    """Health check endpoint for Cloud Run."""
    return jsonify({
        "status": "healthy",
        "service": "Election Education Assistant",
        "version": "1.0.0",
        "gemini_available": model is not None,
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/clear-history", methods=["POST"])
def clear_history():
    """Clear conversation history."""
    session.pop("history", None)
    return jsonify({"message": "History cleared"})


@app.route("/manifest.json")
def manifest():
    """PWA manifest for installable web app."""
    return jsonify({
        "name": "ElectBot - Election Education Assistant",
        "short_name": "ElectBot",
        "description": "Interactive election process education assistant",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0f0f23",
        "theme_color": "#6366f1",
        "icons": [
            {"src": "/static/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icon-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    })


# ─── Error Handlers ──────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    if request.path.startswith("/api/"):
        return jsonify({"error": "Endpoint not found"}), 404
    return render_template("index.html", maps_api_key=MAPS_API_KEY, current_year=datetime.now().year)


@app.errorhandler(429)
def rate_limited(e):
    """Handle rate limit exceeded."""
    return jsonify({"error": "Rate limit exceeded. Please try again later."}), 429


@app.errorhandler(500)
def server_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {e}")
    return jsonify({"error": "Internal server error"}), 500


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_ENV") == "development"
    logger.info(f"🚀 Starting Election Education Assistant on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
