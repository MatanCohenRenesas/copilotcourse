import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide TestClient for all tests"""
    return TestClient(app)
