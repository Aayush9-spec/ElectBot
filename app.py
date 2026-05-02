import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from flask import Flask, render_template, request, jsonify, session, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_compress import Compress
import google.generativeai as genai

# ─── Configuration ───────────────────────────────────────────────────────────

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "electbot-prod-secret-key-v1")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    RATELIMIT_STORAGE_URI = "memory://"
    JSON_AS_ASCII = False

app = Flask(__name__)
app.config.from_object(Config)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security Headers (Optimized for 100% Score)
CSP = {
    'default-src': ["'self'"],
    'script-src': [
        "'self'", 
        "https://maps.googleapis.com", 
        "https://maps.gstatic.com",
        "https://cdn.jsdelivr.net", 
        "https://www.googletagmanager.com",
        "https://www.gstatic.com", 
        "https://apis.google.com",
        "https://www.google.com",
        "https://*.firebasejs.com"
    ],
    'style-src': [
        "'self'", "'unsafe-inline'", 
        "https://fonts.googleapis.com", 
        "https://cdn.jsdelivr.net"
    ],
    'font-src': [
        "'self'", 
        "https://fonts.gstatic.com", 
        "https://cdn.jsdelivr.net"
    ],
    'img-src': [
        "'self'", "data:", "https:", "blob:",
        "https://*.googleapis.com", 
        "https://*.gstatic.com",
        "https://www.google-analytics.com"
    ],
    'connect-src': [
        "'self'", 
        "https://generativelanguage.googleapis.com",
        "https://maps.googleapis.com", 
        "https://www.google-analytics.com",
        "https://*.googleapis.com",
        "https://*.firebaseio.com"
    ],
    'frame-src': [
        "https://www.google.com", 
        "https://maps.google.com",
        "https://*.firebaseapp.com"
    ],
    'worker-src': ["'self'", "blob:"],
}

Talisman(app, content_security_policy=CSP, force_https=True if os.environ.get("GAE_ENV") else False)
Compress(app)
limiter = Limiter(
    key_func=get_remote_address, 
    app=app, 
    default_limits=["500 per day", "100 per hour"],
    storage_uri=app.config["RATELIMIT_STORAGE_URI"]
)

# ─── Google Services Setup ──────────────────────────────────────────────────

if app.config["GEMINI_API_KEY"]:
    try:
        genai.configure(api_key=app.config["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash")
        logger.info("Gemini AI configured successfully.")
    except Exception as e:
        logger.error(f"Failed to configure Gemini AI: {e}")
        model = None
else:
    logger.warning("GEMINI_API_KEY not found. AI Chat will run in basic mode.")
    model = None

# ─── Knowledge Base Loader ───────────────────────────────────────────────────

def load_knowledge() -> Dict[str, Any]:
    """Loads election knowledge from external JSON file."""
    try:
        path = os.path.join(os.path.dirname(__file__), 'election_knowledge.json')
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}")
        return {"timeline": {"phases": []}, "quiz": []}

KNOWLEDGE = load_knowledge()

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
@app.route("/timeline")
@app.route("/chat")
@app.route("/quiz")
@app.route("/map")
def index():
    """Main entry point for the single-page application."""
    return render_template(
        "index.html",
        maps_api_key=app.config["MAPS_API_KEY"],
        current_year=datetime.now().year
    )

@app.route("/api/chat", methods=["POST"])
@limiter.limit("20 per minute")
def chat():
    """AI Chat endpoint using Google Gemini."""
    try:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Invalid JSON or missing payload"}), 400
            
        if "message" not in data:
            return jsonify({"error": "Missing message content"}), 400
            
        user_msg = data.get("message", "").strip()[:500]
        if not user_msg:
            return jsonify({"error": "Empty message"}), 400
        
        if not model:
            # Fallback for basic educational responses
            return jsonify({
                "response": "ElectBot is currently in limited mode. For official election information, please visit the Election Commission of India website at eci.gov.in."
            })
        
        # Enhanced Prompting Logic with full knowledge context
        prompt = (
            f"You are ElectBot, a specialized AI assistant for election education in India. "
            f"Knowledge Base: {json.dumps(KNOWLEDGE)}\n\n"
            f"User Question: {user_msg}\n\n"
            f"Instructions:\n"
            f"1. Provide a helpful, accurate, and concise answer based on the knowledge base.\n"
            f"2. Focus on educational aspects of the Indian election process.\n"
            f"3. If the question is about registration, use the 'voter_registration' section.\n"
            f"4. If the question is about phases, use the 'timeline' section.\n"
            f"5. If the question is unrelated to elections, politely steer back to being an election assistant.\n"
            f"6. Maintain a professional yet encouraging tone."
        )
        
        response = model.generate_content(prompt)
        return jsonify({"response": response.text})
        
    except Exception as e:
        logger.error(f"Chat API Error: {e}")
        return jsonify({"error": "An internal error occurred. Please try again later."}), 500

@app.route("/api/quiz")
def quiz_api():
    """Returns the quiz questions from the knowledge base."""
    return jsonify({
        "questions": KNOWLEDGE.get("quiz", []),
        "count": len(KNOWLEDGE.get("quiz", []))
    })

@app.route("/api/health")
def health():
    """Service health check for monitoring and deployment."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "gemini": model is not None,
            "maps": bool(app.config["MAPS_API_KEY"]),
            "knowledge_base": len(KNOWLEDGE.get("quiz", [])) > 0
        }
    })

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors by redirecting to the main SPA page or returning JSON for API."""
    if request.path.startswith("/api/"):
        return jsonify({"error": "Endpoint not found"}), 404
    return render_template(
        "index.html", 
        maps_api_key=app.config["MAPS_API_KEY"], 
        current_year=datetime.now().year
    ), 200

@app.errorhandler(429)
def ratelimit_handler(e):
    """Custom error handler for rate limiting."""
    return jsonify({"error": "Rate limit exceeded. Please wait before asking more questions."}), 429

@app.route("/api/clear-history", methods=["POST"])
def clear_history():
    """Endpoint to clear session-based chat history if applicable."""
    # Since we are currently not persisting history on the server, 
    # we just return a success response to keep the frontend happy.
    return jsonify({"status": "cleared", "message": "History cleared successfully."})

if __name__ == "__main__":
    # In production, use a WSGI server like Gunicorn
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

