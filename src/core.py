import asyncio
import os
import psycopg

from src.tools.account import db_rbac_check, db_sign_in, db_sign_up, db_change_own_email
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
async def change_own_email(cursor, credentials : dict) -> bool:
    return await db_change_own_email(credentials, cursor)