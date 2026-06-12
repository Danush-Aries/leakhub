"""
Basic integration tests for the LeakHub FastAPI backend.
Uses an in-memory SQLite database so no external services are required.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

# Use in-memory DB for all tests
os.environ.setdefault("DATABASE_URL", "sqlite://")

from apiradar.backend.app.api.main import app
from apiradar.backend.app.core import database as db_module
from apiradar.backend.app.db.models import API, Provider, DiscoverySource


@pytest.fixture(autouse=True)
def setup_in_memory_db(monkeypatch):
    """Replace the engine with a fresh in-memory DB for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    monkeypatch.setattr(db_module, "engine", engine)

    def _get_session():
        return Session(engine)

    monkeypatch.setattr(db_module, "get_session", _get_session)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# System endpoints
# ---------------------------------------------------------------------------

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_ping(client):
    resp = client.get("/ping")
    assert resp.status_code == 200
    assert resp.json() == {"message": "pong"}


# ---------------------------------------------------------------------------
# API catalogue
# ---------------------------------------------------------------------------

def test_list_apis_empty(client):
    resp = client.get("/apis")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["results"] == []


def test_list_apis_with_data(client, setup_in_memory_db):
    engine = setup_in_memory_db
    with Session(engine) as session:
        provider = Provider(name="test-provider")
        session.add(provider)
        session.commit()
        session.refresh(provider)

        api = API(name="Test API", description="A test API", provider_id=provider.id)
        session.add(api)
        session.commit()

    resp = client.get("/apis")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["results"][0]["name"] == "Test API"


def test_search_apis(client, setup_in_memory_db):
    engine = setup_in_memory_db
    with Session(engine) as session:
        api = API(name="Stripe Payments API", description="Payment processing")
        session.add(api)
        session.commit()

    resp = client.get("/apis", params={"search": "Stripe"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

    resp = client.get("/apis", params={"search": "nonexistent"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_get_api_not_found(client):
    resp = client.get("/apis/9999")
    assert resp.status_code == 404


def test_get_api_found(client, setup_in_memory_db):
    engine = setup_in_memory_db
    with Session(engine) as session:
        api = API(name="My API", description="desc", base_url="https://example.com")
        session.add(api)
        session.commit()
        api_id = api.id

    resp = client.get(f"/apis/{api_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "My API"
    assert data["endpoints"] == []


# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

def test_list_providers_empty(client):
    resp = client.get("/providers")
    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------------
# Scrape sources
# ---------------------------------------------------------------------------

def test_list_sources_empty(client):
    resp = client.get("/scrape/sources")
    assert resp.status_code == 200
    assert resp.json() == []
