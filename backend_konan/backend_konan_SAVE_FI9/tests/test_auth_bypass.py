import importlib
import logging

from fastapi.testclient import TestClient

import app.api.auth
import app.main


def _build_client(monkeypatch, test_mode: str, app_env: str | None = None) -> TestClient:
    monkeypatch.setenv("KONAN_TEST_MODE", test_mode)
    if app_env is not None:
        monkeypatch.setenv("APP_ENV", app_env)
    else:
        monkeypatch.delenv("APP_ENV", raising=False)

    importlib.reload(app.api.auth)
    importlib.reload(app.main)
    return TestClient(app.main.app)


def test_me_without_testmode(monkeypatch):
    client = _build_client(monkeypatch, "0", app_env="production")
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_testmode(monkeypatch):
    client = _build_client(monkeypatch, "1", app_env="development")
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test-temp@konan.ai"
    assert data["id"] == 0
    assert data["full_name"] == "Mode Test Sans Auth"
    assert data["plan"] == "FREE"


def test_warning_when_testmode_in_production(monkeypatch, caplog):
    with caplog.at_level(logging.WARNING):
        _build_client(monkeypatch, "1", app_env="production")
    assert any("MODE TEST activé" in record.getMessage() for record in caplog.records)

