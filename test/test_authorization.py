import asyncio
import uuid

import pytest

from src.middleware import authorization_middleware as auth_mod


@pytest.fixture(autouse=True)
def clear_sessions():
    auth_mod._sessions.clear()
    yield
    auth_mod._sessions.clear()


def test_create_session_generates_uuid():
    token = asyncio.run(auth_mod.create_session("user1"))
    uuid_obj = uuid.UUID(token)
    assert str(uuid_obj) == token
    assert auth_mod._sessions[token].username == "user1"


def test_validate_token_for_existing_session():
    token = asyncio.run(auth_mod.create_session("user2"))
    ok, username = asyncio.run(auth_mod.validate_token(token))
    assert ok is True
    assert username == "user2"


def test_validate_token_rejects_missing_session():
    ok, username = asyncio.run(auth_mod.validate_token("00000000-0000-0000-0000-000000000000"))
    assert ok is False
    assert username == ""


def test_validate_token_discards_expired_session():
    token = asyncio.run(auth_mod.create_session("user3"))
    auth_mod._sessions[token].session_init_time -= 3601

    ok, username = asyncio.run(auth_mod.validate_token(token))
    assert ok is False
    assert username == ""
    assert token not in auth_mod._sessions


def test_end_session_removes_user_sessions():
    token = asyncio.run(auth_mod.create_session("user4"))
    asyncio.run(auth_mod.end_session("user4"))
    assert token not in auth_mod._sessions
