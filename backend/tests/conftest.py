import os
import sys
import pytest
from fastapi.testclient import TestClient

# Set testing environment variables before importing app
os.environ["DATABASE_URL"] = "sqlite:///./test_microgrid.db"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from app.database import init_db, Base, engine

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Initialize the database and create all tables
    init_db()
    
    yield
    
    # Teardown
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_microgrid.db"):
        os.remove("./test_microgrid.db")

@pytest.fixture(scope="module")
def client():
    # Use TestClient as context manager to trigger startup/shutdown events
    with TestClient(app) as c:
        yield c
