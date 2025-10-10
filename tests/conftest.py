"""Test configuration and fixtures."""

from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for unit tests."""
    mock = Mock()
    mock.auth = Mock()
    return mock


@pytest.fixture
def client(mock_supabase, monkeypatch):
    """FastAPI test client with mocked Supabase."""
    # Mock the supabase client in app.main
    monkeypatch.setattr("app.main.supabase", mock_supabase)

    from app.main import app

    return TestClient(app)
