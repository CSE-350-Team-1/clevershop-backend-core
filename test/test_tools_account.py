import asyncio

from src.tools import account


class DummyCursor:
    def __init__(self, username_rows=None, email_rows=None):
        self.username_rows = username_rows or []
        self.email_rows = email_rows or []
        self.last_query = None

    def execute(self, sql, params=None):
        self.last_query = sql
        self.last_params = params

    def __iter__(self):
        if "username = %s" in self.last_query:
            return iter(self.username_rows)
        if "email = %s" in self.last_query:
            return iter(self.email_rows)
        return iter([])


def test_db_rbac_check_allows_permitted_task():
    cursor = DummyCursor(username_rows=[("Manager",)])
    assert asyncio.run(account.db_rbac_check("alice", "Manipulate_user", cursor)) is True


def test_db_rbac_check_refuses_forbidden_task():
    cursor = DummyCursor(username_rows=[("User",)])
    assert asyncio.run(account.db_rbac_check("bob", "Manipulate_user", cursor)) is False


def test_db_sign_in_returns_true_when_user_exists():
    cursor = DummyCursor(username_rows=[("alice", "password")])
    assert asyncio.run(account.db_sign_in({"username": "alice", "password": "password"}, cursor)) is True


def test_db_sign_in_returns_false_when_user_missing():
    cursor = DummyCursor()
    assert asyncio.run(account.db_sign_in({"username": "bob", "password": "secret"}, cursor)) is False


def test_db_sign_up_rejects_existing_username_or_email():
    cursor = DummyCursor(username_rows=[("foo",)], email_rows=[("foo@example.com",)])
    result = asyncio.run(
        account.db_sign_up(
            {"username": "foo", "email": "foo@example.com", "password": "secret"},
            cursor,
        )
    )
    assert result["username"] is False
    assert result["email"] is False
    assert result["status"] is False


def test_db_sign_up_accepts_new_user():
    cursor = DummyCursor(username_rows=[], email_rows=[])
    result = asyncio.run(
        account.db_sign_up(
            {"username": "newuser", "email": "new@example.com", "password": "secret"},
            cursor,
        )
    )
    assert result["username"] is True
    assert result["email"] is True
    assert result["status"] is True
