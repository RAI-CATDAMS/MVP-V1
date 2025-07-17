import os, sys
import pytest

# So pytest can find create_app and db
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from app import create_app, db

@pytest.fixture
def app():
    # Each test gets its own in-memory SQLite
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    }
    app = create_app(test_config)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

