import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

import src.core as core
from src.errors.errors import DBError


class DummyConnection:
    def __init__(self):
        self.cursor_obj = MagicMock()
        self.commit = MagicMock()
        self.rollback = MagicMock()

    def cursor(self):
        return self.cursor_obj


def test_db_operation_commits_on_success():
    conn = DummyConnection()
    core.conn = conn

    async def successful_query(cursor):
        assert cursor is conn.cursor_obj
        return "result"

    wrapped = core.db_operation(successful_query)
    assert asyncio.run(wrapped()) == "result"
    conn.commit.assert_called_once()
    conn.rollback.assert_not_called()


def test_db_operation_rolls_back_on_error():
    conn = DummyConnection()
    core.conn = conn

    async def failing_query(cursor):
        raise ValueError("fail")

    wrapped = core.db_operation(failing_query)
    with pytest.raises(DBError):
        asyncio.run(wrapped())

    conn.commit.assert_not_called()
    conn.rollback.assert_called_once()


def test_verify_rbac_calls_db_function(monkeypatch):
    conn = DummyConnection()
    core.conn = conn

    async def fake_db_rbac_check(username, task, cursor):
        assert username == "alice"
        assert task == "Manipulate_self"
        assert cursor is conn.cursor_obj
        return True

    monkeypatch.setattr(
        core, "db_rbac_check", AsyncMock(side_effect=fake_db_rbac_check)
    )

    assert asyncio.run(core.verify_rbac("alice", "Manipulate_self")) is True
    conn.commit.assert_called_once()


def test_sign_in_delegates_to_db_sign_in(monkeypatch):
    conn = DummyConnection()
    core.conn = conn

    async def fake_db_sign_in(credentials, cursor):
        assert credentials["username"] == "bob"
        assert credentials["password"] == "pass"
        assert cursor is conn.cursor_obj
        return True

    monkeypatch.setattr(core, "db_sign_in", AsyncMock(side_effect=fake_db_sign_in))

    assert asyncio.run(core.sign_in({"username": "bob", "password": "pass"})) is True
    conn.commit.assert_called_once()


def test_sign_up_delegates_to_db_sign_up(monkeypatch):
    conn = DummyConnection()
    core.conn = conn

    async def fake_db_sign_up(payload, cursor):
        assert payload["username"] == "carol"
        assert payload["email"] == "carol@example.com"
        assert payload["password"] == "secret"
        assert cursor is conn.cursor_obj
        return {"status": True}

    monkeypatch.setattr(core, "db_sign_up", AsyncMock(side_effect=fake_db_sign_up))

    assert asyncio.run(
        core.sign_up(
            {"username": "carol", "email": "carol@example.com", "password": "secret"}
        )
    ) == {"status": True}
    conn.commit.assert_called_once()
