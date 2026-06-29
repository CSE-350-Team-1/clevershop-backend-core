import asyncio
import os
import psycopg

from src.tools.account import (
    db_rbac_check,
    db_sign_in,
    db_sign_up,
    db_change_own_email,
    db_delete_own_account,
    db_delete_user,
)
from src.tools.service import (
    db_get_items,
    db_list_own_lists,
    db_get_own_list,
    db_add_own_list,
)
from src.errors.errors import DBError

conn_str = None
conn = None
cursor = None


def init_cursor():
    global conn, cursor
    conn = psycopg.connect(conn_str)


def kill_db_connection():
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close()


def db_operation(func):
    async def wrapper(*args, **kwargs):
        global cursor
        cursor = conn.cursor()
        try:
            result = await func(cursor, *args, **kwargs)
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise DBError()
        finally:
            cursor.close()

    return wrapper


@db_operation
async def verify_rbac(cursor, username: str, task: str) -> bool:
    return await db_rbac_check(username, task, cursor)


@db_operation
async def sign_in(cursor, credentials: dict) -> bool:
    return await db_sign_in(credentials, cursor)


@db_operation
async def sign_up(cursor, credentials: dict) -> dict:
    return await db_sign_up(credentials, cursor)


@db_operation
async def change_own_email(cursor, credentials: dict) -> bool:
    return await db_change_own_email(credentials, cursor)


@db_operation
async def delete_own_account(cursor, username: str):
    await db_delete_own_account(username, cursor)


@db_operation
async def delete_user(cursor, username: str) -> dict:
    return await db_delete_user(username, cursor)


@db_operation
async def get_items(cursor) -> list[str]:
    return await db_get_items(cursor)


@db_operation
async def list_own_lists(cursor, username : str) -> list[str]:
    return await db_list_own_lists(username, cursor)


@db_operation
async def get_own_list(cursor, credentials) -> list[list]:
    return await db_get_own_list(credentials, cursor)

@db_operation
async def add_own_list(cursor, credentials : dict) -> dict:
    return await db_add_own_list