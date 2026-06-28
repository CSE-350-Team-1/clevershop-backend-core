import asyncio

from src.rbac.rbac import RBAC_ROLES


# SQL Queries are run here
async def db_rbac_check(username, task, cursor) -> bool:
    user_role = ""
    cursor.execute(f"select Role from People where username = %s", (username,))

    for row in cursor:
        user_role = row[0]

    if task not in RBAC_ROLES.get(user_role):
        return False
    return True


async def db_sign_in(credentials, cursor) -> bool:
    cursor.execute(
        f"select * from People where username = %s AND password = %s",
        (credentials["username"], credentials["password"]),
    )

    for row in cursor:
        return True

    return False


async def db_sign_up(credentials, cursor):
    response = {}

    cursor.execute(
        f"select * from People where username = %s", (credentials["username"])
    )
    for row in cursor:
        response["username"] = False

    cursor.execute(f"select * from People where email = %s", (credentials["email"]))
    for row in cursor:
        response["email"] = False

    if response.get("username") is False or response.get("email") is False:
        response["status"] = False
        return response

    response["username"] = response["email"] = response["status"] = True
    return response


async def db_change_own_email(credentials, cursor) -> bool:
    cursor.execute(
        f"select * from People where email = %s", (credentials.get('email'))
    )
    for row in cursor:
        return False
    
    cursor.execute(
        f"update People set email = %s where username = %s", (credentials.get('email'), credentials.get('username'))
    )

    return True


async def db_delete_own_account(username, cursor):
    cursor.execute(
        f"delete from List_Items where username = %s", (username)
    )

    cursor.execute(
        f"delete from Lists where username = %s", (username)
    )

    cursor.execute(
        f"delete from People where username = %s", (username)
    )
