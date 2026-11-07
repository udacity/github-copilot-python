"""Pytest configuration and fixtures for Sudoku tests."""

import os
import sys
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
STARTER_DIR = os.path.join(ROOT_DIR, "starter")
if STARTER_DIR not in sys.path:
    sys.path.insert(0, STARTER_DIR)

from app import create_app
from domain.game import GameService


@pytest.fixture
def game_service() -> GameService:
    """Provide a fresh GameService instance for each test."""
    return GameService()


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Provide a test client for the app."""
    return app.test_client()

