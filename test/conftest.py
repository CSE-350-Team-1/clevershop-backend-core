"""
This is a shared configuration for both the integration tests and unit tests.
If your tests fail, and you don't know why, you probably broke something here.
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from src.main import app
from src.middleware.error_middleware import LOG_PATH as ORIGINAL_LOG_PATH

# Store the original LOG_PATH globally so we can restore it later
original_log_path = ORIGINAL_LOG_PATH


# Add the test route once to the app (global) and keep it for all tests.
# We'll check if it already exists to avoid duplicates.
def add_test_route():
    for route in app.router.routes:
        if route.path == "/raise-error":
            return  # already present

    @app.get("/raise-error")
    async def raise_error():
        raise Exception("Intentional test exception")


add_test_route()


@pytest.fixture
def temp_log_path(tmp_path: Path):
    """Return a temporary log file path for each test."""
    return tmp_path / "logs" / "error-log.jsonl"


@pytest.fixture
def client(temp_log_path):
    """
    Provide a TestClient with LOG_PATH patched to the temporary location.
    The /raise-error route is already available on the app.
    """
    # Patch the LOG_PATH in the error_middleware module
    import src.middleware.error_middleware

    src.middleware.error_middleware.LOG_PATH = temp_log_path

    yield TestClient(app)

    # Restore the original LOG_PATH after the test (optional)
    src.middleware.error_middleware.LOG_PATH = original_log_path


@pytest.fixture
def clear_log(temp_log_path):
    """Delete the log file before the test starts, if it exists."""
    if temp_log_path.exists():
        temp_log_path.unlink()
    yield
    # No cleanup needed after the test – the temp folder will be removed automatically.
