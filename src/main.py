import asyncio
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core import (
    sign_in,
    sign_up,
    verify_rbac,
    change_own_email,
    delete_own_account,
    delete_user,
    get_items,
    list_own_lists,
    get_own_list,
    add_own_list,
    remove_own_list,
    add_own_item,
    remove_own_item,
)
from src.middleware.authorization_middleware import (
    create_session,
    end_session,
    validate_token,
)
from src.middleware.context_middleware import RequestContext
from src.middleware.error_middleware import Error
from src.errors.errors import AuthorizationError
from src.rbac.rbac import RBAC_ROLES, REQUIRED_ENDPOINT_PERMS

EXEMPT_ROUTES = [
    "/ready"
]  # Where ALL middleware is skipped. Do not forget to account for missing functionality like error handling

NO_AUTH_ROUTES = ["/account/sign_in", "/account/sign_up"]


app = FastAPI()


@app.middleware("http")
async def context_middleware(request: Request, call_next) -> dict:
    if request.url.path in EXEMPT_ROUTES:
        return await call_next(request)

    request_correlation_id = request.headers.get("correlation_id")
    request.state.context = RequestContext(request_correlation_id)

    return await call_next(request)


@app.middleware("http")
async def error_middleware(request: Request, call_next) -> dict:
    if request.url.path in EXEMPT_ROUTES:
        return await call_next(request)

    try:
        return await call_next(request)
    except Exception as e:
        error = Error(request.state.context, str(e))
        error.log_error()

        return JSONResponse(status_code=500, content={"error": str(e)})


@app.middleware("http")
async def authorization_middleware(request: Request, call_next):
    request_path = request.url.path

    if request_path in EXEMPT_ROUTES or request_path in NO_AUTH_ROUTES:
        return await call_next(request)

    # BELOW: Auth key check

    auth_header = request.headers.get("Authorization")
    try:
        if not auth_header:
            raise Exception
        uuid.UUID(auth_header)
    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Authorization header missing or invalid"},
        )

    validation_return = await validate_token(auth_header)
    if validation_return[0] == True:
        request.state.username = validation_return[1]
    else:
        return JSONResponse(
            status_code=401,
            content={"error": "Authorization header missing or invalid"},
        )

    # BELOW: Role checks

    if request_path in REQUIRED_ENDPOINT_PERMS:
        for item in REQUIRED_ENDPOINT_PERMS[request_path]:
            if await verify_rbac(request.state.username, item) != True:
                return JSONResponse(
                    status_code=403, content={"error": "Insufficient permissions"}
                )
    else:
        raise AuthorizationError()

    return await call_next(request)


@app.get("/ready")
async def ready():
    """Server self-test"""

    try:
        response = []
        response.append({"message": "Server is serving"})

        # Add implementation-specific self-test logic here, if necessary. Do not forget error handling

        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/account/sign_in")
async def account_sign_in(
    request: Request,
) -> dict:  # always fails, necessary database is not available yet
    """Expects JSON payload:
    {
    username: str,
    password: str
    }
    """

    input_credentials = await request.json()

    if (
        not isinstance(input_credentials, dict)
        or "username" not in input_credentials
        or "password" not in input_credentials
        or not all(
            item != ""
            for item in [
                input_credentials.get("username"),
                input_credentials.get("password"),
            ]
        )
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid payload; expected JSON{username: str, password: str} with non-empty values"
            },
        )

    function_return = await sign_in(input_credentials)
    if function_return is not True:
        return JSONResponse(
            status_code=401, content={"error": "Incorrect login credentials"}
        )

    access_token = await create_session(input_credentials["username"])
    return {"authorization": access_token}


@app.post("/account/sign_up")
async def account_sign_up(
    request: Request,
) -> dict:  # always fails, necessary database is not available yet
    """Expects JSON payload
    email: str
    username: str
    password: str
    """

    sign_up_payload = await request.json()
    required_fields = {"email", "username", "password"}
    if (
        not isinstance(sign_up_payload, dict)
        or not required_fields.issubset(sign_up_payload.keys())
        or not all(item != "" for item in sign_up_payload.values())
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid payload; expected JSON{email: str, username: str, password: str} with non-empty values"
            },
        )

    sign_up_payload["role"] = "User"
    sign_up_result = await sign_up(sign_up_payload)

    return sign_up_result


@app.post("/account/sign_out")
async def account_sign_out(request: Request) -> dict:
    """No payload"""

    await end_session(request.state.username)

    return {"Status": True}


@app.post("/account/change_own_email")
async def account_change_own_email(request: Request) -> dict:
    """Expects JSON payload
    email: str
    """

    change_own_email_payload = await request.json()

    if (
        not isinstance(change_own_email_payload, dict)
        or not {"email"}.issubset(change_own_email_payload)
        or change_own_email_payload.get("email") == ""
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid payload; expected JSON{email: str} with non-empty values"
            },
        )

    change_own_email_result = await change_own_email(
        {
            "username": request.state.username,
            "email": change_own_email_payload.get("email"),
        }
    )

    if change_own_email_result is False:
        return JSONResponse(status_code=409, content={"error": "Email already exists"})

    return {"status": True}


@app.post("/account/delete_own_account")
async def account_delete_own_account(request: Request):
    """No payload"""

    await delete_own_account(request.state.username)

    return {"status": True}


@app.post("/account/add_user")
async def account_add_user(request: Request):
    """Expects JSON payload
    username: str
    email: str
    password: str"""

    add_user_payload = await request.json()

    required_fields = {"email", "username", "password"}
    if (
        not isinstance(add_user_payload, dict)
        or not required_fields.issubset(add_user_payload.keys())
        or not all(item != "" for item in add_user_payload.values())
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid payload; expected JSON{email: str, username: str, password: str} with non-empty values"
            },
        )

    add_user_payload["role"] = "User"
    add_user_payload_return = await sign_up(add_user_payload)

    if add_user_payload_return.get("status") == False:
        return JSONResponse(status_code=409, content=add_user_payload_return)

    return add_user_payload_return


@app.post("/account/delete_user")
async def account_delete_user(request: Request):
    """Expects JSON payload
    username: str"""

    delete_user_payload = await request.json()

    if (
        not isinstance(delete_user_payload, dict)
        or not {"username"}.issubset(delete_user_payload.keys())
    ) or delete_user_payload.get("username") == "":
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid payload; expected JSON{username: str} with non-empty values"
            },
        )

    delete_user_response = await delete_user(delete_user_payload.get("username"))

    if delete_user_response.get("status") == False:
        return JSONResponse(status_code=404, content={"error": "User not found"})

    return {"status": True}


@app.post("/service/get_items")
async def service_get_items(request: Request) -> list[str]:
    """No payload"""
    return await get_items()


@app.post("/service/list_own_lists")
async def service_list_own_lists(request: Request) -> list[str]:
    """No payload"""
    return await list_own_lists(request.state.username)


@app.post("/service/get_own_list")
async def service_get_own_list(request: Request) -> list[list]:
    """Requires JSON
    list: str

    returns list of lists. Every entry in the bigger list is a list containing a name (str) and bought (bool) (always false for now)
    """

    get_own_list_payload = await request.json()

    if (
        not isinstance(get_own_list_payload, dict)
        or not {"list"}.issubset(get_own_list_payload.keys())
        or get_own_list_payload.get("list") == ""
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid payload; expected JSON{list: str} with non-empty values"
            },
        )

    get_own_list_payload["username"] = request.state.username
    get_own_list_result = await get_own_list(get_own_list_payload)

    if isinstance(get_own_list_result, dict) and get_own_list_result.get("status") == False:
        return JSONResponse(status_code=404, content={"error": "List not found"})

    return get_own_list_result


@app.post("/service/add_own_list")
async def service_add_own_list(request: Request) -> dict:
    """Requires JSON
    list:
    """

    add_own_list_payload = await request.json()

    if (
        not isinstance(add_own_list_payload, dict)
        or not {"list"}.issubset(add_own_list_payload.keys())
        or add_own_list_payload.get("list") == ""
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid payload; expected JSON{list: str} with non-empty values"
            },
        )

    add_own_list_payload["username"] = request.state.username
    add_own_list_result = await add_own_list(add_own_list_payload)

    if add_own_list_result.get("status") == False:
        return JSONResponse(status_code=409, content={"error": "List already exists"})

    return add_own_list_result


@app.post("/service/remove_own_list")
async def service_remove_own_list(request: Request) -> dict:
    """Requires JSON
    list:
    """

    remove_own_list_payload = await request.json()

    if (
        not isinstance(remove_own_list_payload, dict)
        or not {"list"}.issubset(remove_own_list_payload.keys())
        or remove_own_list_payload.get("list") == ""
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid payload; expected JSON{list: str} with non-empty values"
            },
        )

    remove_own_list_payload["username"] = request.state.username
    remove_own_list_result = await remove_own_list(remove_own_list_payload)

    if remove_own_list_result.get("status") == False:
        return JSONResponse(status_code=404, content={"error": "List not found"})

    return remove_own_list_result


@app.post("/service/add_own_item")
async def service_add_own_item(request: Request) -> dict:
    """Requires JSON
    list: listname
    item: itemname
    """

    add_own_item_payload = await request.json()

    if (
        not isinstance(add_own_item_payload, dict)
        or not {"list", "item"}.issubset(add_own_item_payload.keys())
        or not all(item != "" for item in add_own_item_payload.values())
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid payload; expected JSON{list: str, item: str} with non-empty values"
            },
        )

    add_own_item_payload["username"] = request.state.username
    add_own_item_result = await add_own_item(add_own_item_payload)

    if add_own_item_result.get("status") == False:
        return JSONResponse(
            status_code=404, content={"error": "List or item not found"}
        )

    return add_own_item_result


@app.post("/service/remove_own_item")
async def service_remove_own_item(request: Request) -> dict:
    """Requires JSON
    list:
    item:
    """

    remove_own_item_payload = await request.json()

    if (
        not isinstance(remove_own_item_payload, dict)
        or not {"list", "item"}.issubset(remove_own_item_payload.keys())
        or not all(item != "" for item in remove_own_item_payload.values())
    ):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid payload; expected JSON{list: str, item: str} with non-empty values"
            },
        )

    remove_own_item_payload["username"] = request.state.username
    remove_own_item_result = await remove_own_item(remove_own_item_payload)

    if remove_own_item_result.get("status") == False:
        return JSONResponse(
            status_code=404, content={"error": "List or item not found"}
        )

    return remove_own_item_result


# TODO:
# add tests
# remaining service endpoint work can be completed later
