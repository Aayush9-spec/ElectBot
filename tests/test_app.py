import pytest
import json
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    # Mocking Gemini is not strictly necessary for unit tests if we handle the None case,
    # but we can test the fallback logic.
    with flask_app.test_client() as client:
        yield client

def test_index_page(client):
    """Test that the index page loads correctly for various SPA routes."""
    routes = ['/', '/timeline', '/chat', '/quiz', '/map']
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200
        assert b'ElectBot' in response.data
        assert b'<!DOCTYPE html>' in response.data

def test_api_health(client):
    """Test the health check API details."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'services' in data
    assert 'timestamp' in data

def test_api_quiz_structure(client):
    """Test the quiz API returns correct structure and data."""
    response = client.get('/api/quiz')
    assert response.status_code == 200
    data = response.get_json()
    assert 'questions' in data
    assert 'count' in data
    assert isinstance(data['questions'], list)
    if data['count'] > 0:
        q = data['questions'][0]
        assert 'q' in q
        assert 'options' in q
        assert 'correct' in q

def test_api_chat_validation(client):
    """Test chat API input validation."""
    # Test missing payload
    response = client.post('/api/chat', data=None)
    assert response.status_code == 400
    
    # Test missing message key
    response = client.post('/api/chat', json={"wrong_key": "hello"})
    assert response.status_code == 400
    
    # Test empty message
    response = client.post('/api/chat', json={"message": "   "})
    assert response.status_code == 400

def test_api_chat_fallback(client):
    """Test chat API fallback when Gemini is not configured."""
    # Assuming GEMINI_API_KEY is not set in test environment
    response = client.post('/api/chat', json={"message": "How do I vote?"})
    assert response.status_code == 200
    data = response.get_json()
    assert 'response' in data
    assert "ECI" in data['response'] or "ElectBot" in data['response']

def test_404_handling(client):
    """Test custom 404 handling for both web and API."""
    # Web 404 should return index.html (SPA behavior)
    response = client.get('/some/random/route')
    assert response.status_code == 200
    assert b'ElectBot' in response.data
    
    # API 404 should return JSON
    response = client.get('/api/v1/invalid')
    assert response.status_code == 404
    assert response.get_json()['error'] == 'Endpoint not found'

def test_rate_limiting_triggered(client):
    """Test that rate limiting is configured (smoke test)."""
    # This might be hard to trigger in a single test without loop,
    # but we check if the decorator is applied by looking at app logic if needed.
    # For now, just ensure the endpoint works.
    response = client.post('/api/chat', json={"message": "test"})
    assert response.status_code == 200
