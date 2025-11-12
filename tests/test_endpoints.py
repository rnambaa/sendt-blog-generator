import sys
from pathlib import Path
# add root dir 
root = str(Path(__file__).parent.parent)
print(root)
sys.path.insert(0, root)

from fastapi.testclient import TestClient
import pytest
from api.main import app


client = TestClient(app)

def test_health_check(): 
    """Test the /health endpoint"""
    response = client.get("/health")

    assert response.status_code == 200
    print(f"Health response: {response.json()}")

def test_set_tone_endpoint():
    """Test the /tone endpoint with dummy data"""
    dummy_request = {
        "tone": "professional"
    }
    
    response = client.post("/settings/tone", json=dummy_request)
    
    assert response.status_code == 200
    print(f"Tone response: {response.json()}")


def test_generate_blog():
    """Test the /generate endpoint with dummy data"""
    dummy_request = {
        "purpose": "Introduce smart televisions to our clients.",
        "language": "english"
    }
    
    response = client.post("/generate", json=dummy_request)
    print(response)
    
    assert response.status_code == 200
    print(response.json())


def test_generate_blog_default_language():
    """Test generate endpoint without specifying language (should default to english)"""
    dummy_request = {
        "purpose": "Introduce smart televisions to our clients."
    }
    
    response = client.post("/generate", json=dummy_request)
    
    assert response.status_code == 200
    print(f"Default language response: {response.json()}")


def test_invalid_requests():
    """Test endpoints with invalid data to see error handling"""
    # Missing required field for generate
    response = client.post("/generate", json={"language": "english"})
    assert response.status_code == 422
    print(f"Missing purpose error: {response.json()}")
    
    # Missing required field for tone
    response = client.post("/settings/tone", json={})
    assert response.status_code == 422
    print(f"Missing tone error: {response.json()}")