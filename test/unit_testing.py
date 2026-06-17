import json
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import src.main


# TC‑01: Verifies the health endpoint works – critical for deployment checks.
def test_ready_success(client: TestClient):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == [{"message": "Server is serving"}]


# TC‑02: Confirms /ready is exempt from error middleware.
def test_ready_exempt_from_error_middleware():
    assert "/ready" in src.main.EXEMPT_ROUTES


# TC‑03: Ensures a valid UUIDv4 is auto‑generated when no correlation ID is sent.
def test_missing_correlation_id(client: TestClient, temp_log_path: Path, clear_log):
    response = client.get("/raise-error")
    assert response.status_code == 500

    assert temp_log_path.exists()
    with open(temp_log_path) as f:
        log_entry = json.loads(f.readlines()[-1])

    cid = log_entry["correlation_id"]
    try:
        uuid.UUID(cid, version=4)
    except ValueError:
        pytest.fail(f"Not a valid UUIDv4: {cid}")

    assert "request_time" in log_entry
    assert "error_time" in log_entry
    assert "message" in log_entry


# TC‑04: Validates that a provided (valid) correlation ID is used exactly.
def test_provided_correlation_id(client: TestClient, temp_log_path: Path, clear_log):
    test_cid = "123e4567-e89b-12d3-a456-426614174000"  # valid UUIDv4
    client.get("/raise-error", headers={"correlation_id": test_cid})

    assert temp_log_path.exists()
    with open(temp_log_path) as f:
        log_entry = json.loads(f.readlines()[-1])

    assert log_entry["correlation_id"] == test_cid


# TC‑04b: Ensures malformed UUIDs are discarded and replaced with a valid one.
def test_invalid_correlation_id(client: TestClient, temp_log_path: Path, clear_log):
    bad_cid = "this-is-not-a-uuid"
    client.get("/raise-error", headers={"correlation_id": bad_cid})

    with open(temp_log_path) as f:
        log_entry = json.loads(f.readlines()[-1])

    logged_cid = log_entry["correlation_id"]
    assert logged_cid != bad_cid

    try:
        uuid.UUID(logged_cid, version=4)
    except ValueError:
        pytest.fail(f"Generated invalid UUID: {logged_cid}")


# TC‑05: Confirms error logs contain all required fields for monitoring/debugging.
def test_unhandled_exception_logging(
    client: TestClient, temp_log_path: Path, clear_log
):
    client.get("/raise-error")

    assert temp_log_path.exists()
    with open(temp_log_path) as f:
        log_entry = json.loads(f.readlines()[-1])

    assert log_entry["type"] == "error"
    assert "correlation_id" in log_entry
    assert "request_time" in log_entry
    assert "error_time" in log_entry
    assert "message" in log_entry


# TC‑06: Ensures the logs folder and file are auto‑created on first error.
def test_log_file_creation(client: TestClient, temp_log_path: Path):
    if temp_log_path.parent.exists():
        import shutil

        shutil.rmtree(temp_log_path.parent)

    assert not temp_log_path.parent.exists()

    client.get("/raise-error")

    assert temp_log_path.parent.exists()
    assert temp_log_path.exists()


# TC‑08: Documents that /ready bypasses middleware – confirmed by TC‑02.
def test_middleware_exemption():
    # The exemption is already verified in test_ready_exempt_from_error_middleware.
    pass
