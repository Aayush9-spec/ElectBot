"""
Test suite for Election Education Assistant.
Covers API endpoints, security, and knowledge base functionality.
"""

import pytest
import json
from app import app, ELECTION_KNOWLEDGE, sanitize_input, get_fallback_response


@pytest.fixture
def client():
    """Create a test client."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_returns_200(self, client):
        res = client.get('/api/health')
        assert res.status_code == 200
        data = json.loads(res.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'Election Education Assistant'
        assert 'version' in data
        assert 'timestamp' in data

    def test_health_includes_gemini_status(self, client):
        res = client.get('/api/health')
        data = json.loads(res.data)
        assert 'gemini_available' in data


class TestIndexPage:
    """Test main page rendering."""

    def test_index_returns_200(self, client):
        res = client.get('/')
        assert res.status_code == 200
        assert b'ElectBot' in res.data

    def test_index_has_accessibility(self, client):
        res = client.get('/')
        assert b'skip-link' in res.data
        assert b'aria-label' in res.data
        assert b'role="main"' in res.data

    def test_index_has_meta_tags(self, client):
        res = client.get('/')
        assert b'<meta name="description"' in res.data
        assert b'<meta name="viewport"' in res.data


class TestChatAPI:
    """Test chat endpoint."""

    def test_chat_requires_message(self, client):
        res = client.post('/api/chat', json={})
        assert res.status_code == 400

    def test_chat_rejects_empty_message(self, client):
        res = client.post('/api/chat', json={'message': ''})
        assert res.status_code == 400

    def test_chat_returns_response(self, client):
        res = client.post('/api/chat', json={'message': 'How to register?'})
        assert res.status_code == 200
        data = json.loads(res.data)
        assert 'response' in data
        assert 'timestamp' in data

    def test_chat_handles_registration_query(self, client):
        res = client.post('/api/chat', json={'message': 'voter registration'})
        data = json.loads(res.data)
        assert 'response' in data

    def test_chat_handles_timeline_query(self, client):
        res = client.post('/api/chat', json={'message': 'election timeline'})
        data = json.loads(res.data)
        assert 'response' in data


class TestKnowledgeAPI:
    """Test knowledge base endpoint."""

    def test_get_timeline(self, client):
        res = client.get('/api/knowledge/timeline')
        assert res.status_code == 200
        data = json.loads(res.data)
        assert 'data' in data
        assert 'phases' in data['data']

    def test_get_voter_registration(self, client):
        res = client.get('/api/knowledge/voter_registration')
        assert res.status_code == 200

    def test_get_voting_methods(self, client):
        res = client.get('/api/knowledge/voting_methods')
        assert res.status_code == 200

    def test_get_invalid_category(self, client):
        res = client.get('/api/knowledge/nonexistent')
        assert res.status_code == 404


class TestQuizAPI:
    """Test quiz endpoint."""

    def test_quiz_returns_questions(self, client):
        res = client.get('/api/quiz')
        assert res.status_code == 200
        data = json.loads(res.data)
        assert 'questions' in data
        assert len(data['questions']) == 10

    def test_quiz_question_format(self, client):
        res = client.get('/api/quiz')
        data = json.loads(res.data)
        q = data['questions'][0]
        assert 'question' in q
        assert 'options' in q
        assert 'correct' in q
        assert 'explanation' in q
        assert len(q['options']) == 4


class TestSecurity:
    """Test security features."""

    def test_sanitize_input_strips_html(self):
        result = sanitize_input('<script>alert("xss")</script>Hello')
        assert '<script>' not in result
        assert 'Hello' in result

    def test_sanitize_input_limits_length(self):
        result = sanitize_input('A' * 3000)
        assert len(result) == 2000

    def test_sanitize_empty_input(self):
        assert sanitize_input('') == ''
        assert sanitize_input(None) == ''

    def test_security_headers(self, client):
        res = client.get('/')
        assert res.headers.get('X-Content-Type-Options') == 'nosniff'


class TestKnowledgeBase:
    """Test knowledge base data integrity."""

    def test_timeline_has_phases(self):
        assert len(ELECTION_KNOWLEDGE['timeline']['phases']) == 8

    def test_voter_registration_has_steps(self):
        assert len(ELECTION_KNOWLEDGE['voter_registration']['steps']) == 6

    def test_voting_methods_has_entries(self):
        assert len(ELECTION_KNOWLEDGE['voting_methods']['methods']) >= 3

    def test_election_types_has_entries(self):
        assert len(ELECTION_KNOWLEDGE['election_types']['types']) >= 5

    def test_faqs_exist(self):
        assert len(ELECTION_KNOWLEDGE['faqs']) >= 5


class TestFallbackResponses:
    """Test fallback response logic."""

    def test_registration_fallback(self):
        resp = get_fallback_response("How to register as voter?")
        assert 'registration' in resp.lower() or 'register' in resp.lower() or 'Step' in resp

    def test_timeline_fallback(self):
        resp = get_fallback_response("election timeline")
        assert 'Phase' in resp or 'Timeline' in resp

    def test_voting_fallback(self):
        resp = get_fallback_response("How does EVM work?")
        assert 'EVM' in resp or 'Electronic' in resp

    def test_default_fallback(self):
        resp = get_fallback_response("random unrelated text xyz123")
        assert 'ElectBot' in resp


class TestClearHistory:
    """Test chat history clearing."""

    def test_clear_history(self, client):
        res = client.post('/api/clear-history')
        assert res.status_code == 200
        data = json.loads(res.data)
        assert 'message' in data


class TestErrorHandlers:
    """Test error handling."""

    def test_404_api(self, client):
        res = client.get('/api/nonexistent')
        assert res.status_code == 404

    def test_404_page_returns_index(self, client):
        res = client.get('/nonexistent-page')
        assert res.status_code == 200
