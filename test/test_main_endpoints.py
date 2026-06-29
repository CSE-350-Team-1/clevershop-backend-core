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


def test_change_own_email_requires_authorization(client: TestClient):
    response = client.post(
        "/account/change_own_email", json={"email": "new@example.com"}
    )
    assert response.status_code == 401


def test_change_own_email_succeeds_with_valid_token(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_change_own_email(payload):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "change_own_email", fake_change_own_email)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/account/change_own_email",
        headers={"Authorization": token},
        json={"email": "new@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": True}


def test_change_own_email_conflict_returns_409(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_change_own_email(payload):
        return False

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "change_own_email", fake_change_own_email)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/account/change_own_email",
        headers={"Authorization": token},
        json={"email": "new@example.com"},
    )

    assert response.status_code == 409
    assert response.json() == {"error": "Email already exists"}


def test_delete_own_account_requires_authorization(client: TestClient):
    response = client.post("/account/delete_own_account")
    assert response.status_code == 401


def test_delete_own_account_succeeds_with_valid_token(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_delete_own_account(username):
        return None

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "delete_own_account", fake_delete_own_account)

    token = asyncio.run(create_session("user2"))
    response = TestClient(main.app).post(
        "/account/delete_own_account",
        headers={"Authorization": token},
    )

    assert response.status_code == 200
    assert response.json() == {"status": True}


def test_add_user_requires_authorization(client: TestClient):
    response = client.post(
        "/account/add_user",
        json={"username": "user3", "email": "user3@example.com", "password": "pass"},
    )
    assert response.status_code == 401


def test_add_user_succeeds_with_valid_token(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_sign_up(payload):
        return {"status": True}

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "sign_up", fake_sign_up)

    token = asyncio.run(create_session("manager1"))
    response = TestClient(main.app).post(
        "/account/add_user",
        headers={"Authorization": token},
        json={"username": "user3", "email": "user3@example.com", "password": "pass"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": True}


def test_add_user_conflict_returns_409(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_sign_up(payload):
        return {"status": False, "error": "Username already exists"}

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "sign_up", fake_sign_up)

    token = asyncio.run(create_session("manager1"))
    response = TestClient(main.app).post(
        "/account/add_user",
        headers={"Authorization": token},
        json={"username": "user3", "email": "user3@example.com", "password": "pass"},
    )

    assert response.status_code == 409
    assert response.json() == {"status": False, "error": "Username already exists"}


def test_delete_user_requires_authorization(client: TestClient):
    response = client.post(
        "/account/delete_user",
        json={"username": "user4"},
    )
    assert response.status_code == 401


def test_delete_user_succeeds_with_valid_token(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_delete_user(username):
        return {"status": True}

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "delete_user", fake_delete_user)

    token = asyncio.run(create_session("manager1"))
    response = TestClient(main.app).post(
        "/account/delete_user",
        headers={"Authorization": token},
        json={"username": "user4"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": True}


def test_delete_user_not_found_returns_404(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_delete_user(username):
        return {"status": False}

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "delete_user", fake_delete_user)

    token = asyncio.run(create_session("manager1"))
    response = TestClient(main.app).post(
        "/account/delete_user",
        headers={"Authorization": token},
        json={"username": "user4"},
    )

    assert response.status_code == 404
    assert response.json() == {"error": "User not found"}


def test_get_items_requires_authorization(client: TestClient):
    response = client.post("/service/get_items")
    assert response.status_code == 401


def test_get_items_succeeds_with_valid_token(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_get_items():
        return ["Item1", "Item2", "Item3"]

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "get_items", fake_get_items)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/get_items",
        headers={"Authorization": token},
    )

    assert response.status_code == 200
    assert response.json() == ["Item1", "Item2", "Item3"]


def test_list_own_lists_requires_authorization(client: TestClient):
    response = client.post("/service/list_own_lists")
    assert response.status_code == 401


def test_list_own_lists_succeeds_with_valid_token(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_list_own_lists(username):
        if username == "user1":
            return ["Shopping", "ToDo"]
        return []

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "list_own_lists", fake_list_own_lists)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/list_own_lists",
        headers={"Authorization": token},
    )

    assert response.status_code == 200
    assert response.json() == ["Shopping", "ToDo"]


def test_list_own_lists_returns_empty_list(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_list_own_lists(username):
        return []

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "list_own_lists", fake_list_own_lists)

    token = asyncio.run(create_session("newuser"))
    response = TestClient(main.app).post(
        "/service/list_own_lists",
        headers={"Authorization": token},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_own_list_requires_authorization(client: TestClient):
    response = client.post(
        "/service/get_own_list",
        json={"list": "Shopping"},
    )
    assert response.status_code == 401


def test_get_own_list_rejects_missing_list_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/get_own_list",
        headers={"Authorization": token},
        json={"wrong_field": "Shopping"},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_get_own_list_rejects_empty_list_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/get_own_list",
        headers={"Authorization": token},
        json={"list": ""},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_get_own_list_rejects_non_dict_payload(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/get_own_list",
        headers={"Authorization": token},
        json="not a dict",
    )

    assert response.status_code == 400


def test_get_own_list_succeeds_with_valid_payload(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_get_own_list(credentials):
        return [["milk", False], ["bread", True]]

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "get_own_list", fake_get_own_list)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/get_own_list",
        headers={"Authorization": token},
        json={"list": "Shopping"},
    )

    assert response.status_code == 200
    assert response.json() == [["milk", False], ["bread", True]]


def test_get_own_list_not_found_returns_404(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_get_own_list(credentials):
        return {"status": False}

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "get_own_list", fake_get_own_list)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/get_own_list",
        headers={"Authorization": token},
        json={"list": "NonexistentList"},
    )

    assert response.status_code == 404
    assert response.json() == {"error": "List not found"}


def test_add_own_list_requires_authorization(client: TestClient):
    response = client.post(
        "/service/add_own_list",
        json={"list": "NewList"},
    )
    assert response.status_code == 401


def test_add_own_list_rejects_missing_list_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/add_own_list",
        headers={"Authorization": token},
        json={"wrong_field": "NewList"},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_add_own_list_rejects_empty_list_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/add_own_list",
        headers={"Authorization": token},
        json={"list": ""},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_add_own_list_succeeds_with_valid_payload(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_add_own_list(credentials):
        return {"status": True}

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "add_own_list", fake_add_own_list)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/add_own_list",
        headers={"Authorization": token},
        json={"list": "NewList"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": True}


def test_add_own_list_conflict_returns_409(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_add_own_list(credentials):
        return {"status": False}

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "add_own_list", fake_add_own_list)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/add_own_list",
        headers={"Authorization": token},
        json={"list": "ExistingList"},
    )

    assert response.status_code == 409
    assert response.json() == {"error": "List already exists"}


def test_remove_own_list_requires_authorization(client: TestClient):
    response = client.post(
        "/service/remove_own_list",
        json={"list": "ListToDelete"},
    )
    assert response.status_code == 401


def test_remove_own_list_rejects_missing_list_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/remove_own_list",
        headers={"Authorization": token},
        json={"wrong_field": "ListToDelete"},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_remove_own_list_rejects_empty_list_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/remove_own_list",
        headers={"Authorization": token},
        json={"list": ""},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_remove_own_list_succeeds_with_valid_payload(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_remove_own_list(credentials):
        return {"status": True}

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "remove_own_list", fake_remove_own_list)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/remove_own_list",
        headers={"Authorization": token},
        json={"list": "ListToDelete"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": True}


def test_remove_own_list_not_found_returns_404(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_remove_own_list(credentials):
        return {"status": False}

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "remove_own_list", fake_remove_own_list)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/remove_own_list",
        headers={"Authorization": token},
        json={"list": "NonexistentList"},
    )

    assert response.status_code == 404
    assert response.json() == {"error": "List not found"}


def test_add_own_item_requires_authorization(client: TestClient):
    response = client.post(
        "/service/add_own_item",
        json={"list": "Shopping", "item": "milk"},
    )
    assert response.status_code == 401


def test_add_own_item_rejects_missing_list_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/add_own_item",
        headers={"Authorization": token},
        json={"item": "milk"},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_add_own_item_rejects_missing_item_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/add_own_item",
        headers={"Authorization": token},
        json={"list": "Shopping"},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_add_own_item_rejects_empty_list_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/add_own_item",
        headers={"Authorization": token},
        json={"list": "", "item": "milk"},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_add_own_item_rejects_empty_item_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/add_own_item",
        headers={"Authorization": token},
        json={"list": "Shopping", "item": ""},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_add_own_item_succeeds_with_valid_payload(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_add_own_item(credentials):
        return {"status": True}

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "add_own_item", fake_add_own_item)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/add_own_item",
        headers={"Authorization": token},
        json={"list": "Shopping", "item": "milk"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": True}


def test_add_own_item_not_found_returns_404(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_add_own_item(credentials):
        return {"status": False}

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "add_own_item", fake_add_own_item)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/add_own_item",
        headers={"Authorization": token},
        json={"list": "Shopping", "item": "milk"},
    )

    assert response.status_code == 404
    assert response.json() == {"error": "List or item not found"}


def test_remove_own_item_requires_authorization(client: TestClient):
    response = client.post(
        "/service/remove_own_item",
        json={"list": "Shopping", "item": "milk"},
    )
    assert response.status_code == 401


def test_remove_own_item_rejects_missing_list_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/remove_own_item",
        headers={"Authorization": token},
        json={"item": "milk"},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_remove_own_item_rejects_missing_item_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/remove_own_item",
        headers={"Authorization": token},
        json={"list": "Shopping"},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_remove_own_item_rejects_empty_list_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/remove_own_item",
        headers={"Authorization": token},
        json={"list": "", "item": "milk"},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_remove_own_item_rejects_empty_item_field(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/remove_own_item",
        headers={"Authorization": token},
        json={"list": "Shopping", "item": ""},
    )

    assert response.status_code == 400
    assert "Invalid payload" in response.json()["error"]


def test_remove_own_item_succeeds_with_valid_payload(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_remove_own_item(credentials):
        return {"status": True}

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "remove_own_item", fake_remove_own_item)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/remove_own_item",
        headers={"Authorization": token},
        json={"list": "Shopping", "item": "milk"},
    )

    assert response.status_code == 200
    assert response.json() == {"status": True}


def test_remove_own_item_not_found_returns_404(monkeypatch):
    async def fake_verify_rbac(username, permission):
        return True

    async def fake_remove_own_item(credentials):
        return {"status": False}

    monkeypatch.setattr(main, "verify_rbac", fake_verify_rbac)
    monkeypatch.setattr(main, "remove_own_item", fake_remove_own_item)

    token = asyncio.run(create_session("user1"))
    response = TestClient(main.app).post(
        "/service/remove_own_item",
        headers={"Authorization": token},
        json={"list": "Shopping", "item": "milk"},
    )

    assert response.status_code == 404
    assert response.json() == {"error": "List or item not found"}
