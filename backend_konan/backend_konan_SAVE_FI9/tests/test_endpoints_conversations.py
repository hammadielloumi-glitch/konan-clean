# tests/test_endpoints_conversations.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_conversations.db"

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_1_create_conversation():
    payload = {"title": "Test conversation"}
    r = client.post("/api/conversations", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert data["title"] == "Test conversation"
    global CONV_ID
    CONV_ID = data["id"]


def test_2_list_conversations():
    r = client.get("/api/conversations?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert any("id" in c for c in data["items"])


def test_3_patch_conversation():
    payload = {"title": "Renommée depuis test"}
    r = client.patch(f"/api/conversations/{CONV_ID}", json=payload)
    assert r.status_code == 200
    r2 = client.get("/api/conversations")
    titles = [c["message_user"] for c in r2.json()["items"]]
    assert any("Renommée" in t for t in titles)


def test_4_get_conversation_messages():
    r = client.get(f"/api/conversations/{CONV_ID}/messages?limit=10")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_5_delete_conversation():
    r = client.delete(f"/api/conversations/{CONV_ID}")
    assert r.status_code == 200 or r.status_code == 204
    r2 = client.get("/api/conversations")
    assert CONV_ID not in [c["id"] for c in r2.json()["items"]]
