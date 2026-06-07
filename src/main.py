import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.middleware.context_middleware import RequestContext
from src.middleware.error_middleware import Error

EXEMPT_ROUTES = [
    "/ready"
]  # Where middleware is skipped. Do not forget to account for missing functionality like error handling
app = FastAPI()


@app.middleware("http")
async def context_middleware(request: Request, call_next):
    if request.url.path in EXEMPT_ROUTES:
        return await call_next(request)

    request_correlation_id = request.headers.get("correlation_id")
    request.state.context = RequestContext(request_correlation_id)

    return await call_next(request)


@app.middleware("http")
async def error_middleware(request: Request, call_next):
    if request.url.path in EXEMPT_ROUTES:
        return await call_next(request)

    try:
        return await call_next(request)
    except Exception as e:
        error = Error(request.state.context, str(e))
        error.log_error()

        return JSONResponse(status_code=500, content={"error": str(e)})


# add new middleware here (e.g. authentication_middleware)


@app.get("/ready")
async def ready():
    """Server self-test"""

    try:
        response = []
        response.append({"message": "Server is serving"})

        # Add implementation-specific self-test logic here. Do not forget error handling

        return response
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# add new endpoints here
