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

async def db_get_own_list(credentials, cursor) -> list[list]:
    return_list = []
    cursor.execute("select (item_name, bought) from list_items where username = %s and list_name = %s", (credentials.get('username'), credentials.get('list'),))

    found_flag = False
    for row in cursor:
        found_flag = True

        return_list.append([row[0], row[1]])

    if not found_flag:
        return {'status' : False}
    
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

    