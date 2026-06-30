import asyncio
from datetime import datetime


def get_current_date():
    return datetime.now().date()


async def db_get_items(cursor) -> list[str]:
    return_list = []
    cursor.execute("select * from Items")
    for row in cursor:
        return_list.append(row[0])

    return return_list


async def db_list_own_lists(username, cursor) -> list[str]:
    return_list = []
    cursor.execute("select * from Lists where username = %s", (username,))

    for row in cursor:
        return_list.append(row[0])

    return return_list

# This function does a db call to get lists, with the correct credentials, and now also gets empty lists.
async def db_get_own_list(credentials, cursor) -> list[list]:
    return_list = []
    cursor.execute(
        "SELECT item_name, bought FROM list_items WHERE username = %s AND list_name = %s",
        (
            credentials.get("username"),
            credentials.get("list"),
        ),
    )

    found_flag = False
    for row in cursor:
        found_flag = True
        return_list.append([row[0], row[1]])

    if not found_flag:
        # Check if the list exists in the lists table
        cursor.execute(
            "SELECT * FROM lists WHERE username = %s AND list_name = %s",
            (credentials.get("username"), credentials.get("list")),
        )
        list_exists = cursor.fetchall()

        if not list_exists:
            return {"status": False}  # List doesn't exist at all
        else:
            return []  # User may create an empty list and could edit it later.

    return return_list


async def db_add_own_list(credentials, cursor) -> dict:
    cursor.execute(
        "select * from lists where username = %s and list_name = %s",
        (credentials.get("username"), credentials.get("list")),
    )

    for row in cursor:
        return {"status": False}

    current_date = get_current_date()
    cursor.execute(
        "insert into lists (username, list_name, creation_date) values (%s, %s, %s)",
        (credentials.get("username"), credentials.get("list"), current_date),
    )
    return {"status": True}


async def db_remove_own_list(credentials, cursor) -> dict:
    cursor.execute(
        "select * from lists where username = %s and list_name = %s",
        (
            credentials.get("username"),
            credentials.get("list"),
        ),
    )

    exist_flag = False

    for row in cursor:
        exist_flag = True

    if not exist_flag:
        return {"status": False}

    cursor.execute(
        "delete from list_items where username = %s and list_name = %s",
        (
            credentials.get("username"),
            credentials.get("list"),
        ),
    )
    cursor.execute(
        "delete from lists where username = %s and list_name = %s",
        (
            credentials.get("username"),
            credentials.get("list"),
        ),
    )

    return {"status": True}


async def db_add_own_item(credentials, cursor) -> dict:
    cursor.execute(
        "select * from items where item_name = %s", (credentials.get("item"),)
    )

    exist_flag = False

    for row in cursor:
        exist_flag = True

    if not exist_flag:
        return {"status": False}

    cursor.execute(
        "select * from lists where username = %s and list_name = %s",
        (
            credentials.get("username"),
            credentials.get("list"),
        ),
    )
    exist_flag = False

    for row in cursor:
        exist_flag = True

    if not exist_flag:
        return {"status": False}

    cursor.execute(
        "insert into list_items (item_name, list_name, username, bought) values (%s, %s, %s, false)",
        (
            credentials.get("item"),
            credentials.get("list"),
            credentials.get("username"),
        ),
    )

    return {"status": True}


async def db_remove_own_item(credentials, cursor) -> dict:
    cursor.execute(
        "select * from list_items where item_name = %s and list_name = %s and username = %s",
        (credentials.get("item"), credentials.get("list"), credentials.get("username")),
    )

    exit_flag = False

    for row in cursor:
        exist_flag = True

    if not exist_flag:
        return {"status": False}

    cursor.execute(
        "delete from list_items where item_name = %s and list_name = %s and username = %s",
        (credentials.get("item"), credentials.get("list"), credentials.get("username")),
    )

    return {"status": True}
