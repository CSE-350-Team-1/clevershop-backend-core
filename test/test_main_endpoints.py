import asyncio
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

import src.main as main
from src.middleware.authorization_middleware import create_session, _sessions


def test_sign_in_rejects_invalid_payload(client: TestClient):
    response = client.post("/account/sign_in", json={"username": "user1"})
    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_sign_in_returns_authorization_token(monkeypatch, client: TestClient):
    async def fake_sign_in(credentials):
        return True

    async def fake_create_session(username):
        return "fake-token"

    monkeypatch.setattr(main, "sign_in", fake_sign_in)
    monkeypatch.setattr(main, "create_session", fake_create_session)

    response = client.post(
        "/account/sign_in",
        json={"username": "user1", "password": "password"},
    )

    assert response.status_code == 200
    assert response.json() == {"authorization": "fake-token"}


def test_sign_up_rejects_invalid_payload(client: TestClient):
    response = client.post(
        "/account/sign_up", json={"username": "user1", "password": "password"}
    )
    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_sign_up_forwards_payload(monkeypatch, client: TestClient):
    async def fake_sign_up(payload):
        return {"status": True}

    monkeypatch.setattr(main, "sign_up", fake_sign_up)

    response = client.post(
        "/account/sign_up",
        json={"username": "user1", "email": "test@example.com", "password": "password"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": True}


def test_sign_out_requires_authorization(client: TestClient):
    response = client.post("/account/sign_out")
    assert response.status_code == 401


def test_sign_out_succeeds_with_valid_token():
    token = asyncio.run(create_session("user5"))
    response = TestClient(main.app).post(
        "/account/sign_out", headers={"Authorization": token}
    )
    assert response.status_code == 200
    assert response.json() == {"Status": True}
    assert token not in _sessions
