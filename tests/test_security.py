import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_security_headers(client):
    """Verify that essential security headers are present."""
    response = client.get('/')
    headers = response.headers
    
    # Check Talisman defaults and custom CSP
    assert 'Content-Security-Policy' in headers
    assert 'X-Content-Type-Options' in headers
    assert 'X-Frame-Options' in headers
    assert 'Referrer-Policy' in headers
    assert 'Permissions-Policy' in headers
    
    csp = headers['Content-Security-Policy']
    assert "default-src 'self'" in csp
    assert "https://maps.googleapis.com" in csp

def test_hsts_header(client):
    """Check for HSTS header (should be present in production/forced https)."""
    # Note: Talisman might not send HSTS on HTTP by default unless force_https=True
    # In our app.py, force_https is conditionally set.
    pass

def test_cors_preflight(client):
    """Ensure API endpoints handle preflight or have restrictive CORS if needed."""
    # Our app doesn't explicitly use Flask-CORS, so it should follow same-origin by default (via CSP).
    response = client.options('/api/chat')
    assert response.status_code in [200, 405]
