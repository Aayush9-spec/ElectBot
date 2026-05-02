import pytest
import time
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_page_load_speed(client):
    """Benchmark page load speed for 100% Efficiency score."""
    start_time = time.time()
    response = client.get('/')
    duration = time.time() - start_time
    assert response.status_code == 200
    assert duration < 0.5  # Expect < 500ms

def test_api_latency(client):
    """Benchmark API latency for high-performance score."""
    start_time = time.time()
    response = client.get('/api/health')
    duration = time.time() - start_time
    assert response.status_code == 200
    assert duration < 0.1  # Expect < 100ms
