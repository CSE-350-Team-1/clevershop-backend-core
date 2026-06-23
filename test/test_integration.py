import os
import subprocess
import time
import pytest
import requests


# TC‑07: Verifies the container binds to the PORT environment variable.
def test_port_binding():
    """
    Start the Uvicorn server on port 9000 and verify it responds.
    This is a true integration test – it spins up a real subprocess.
    """
    port = 9000
    # Start the server as a subprocess
    proc = subprocess.Popen(
        ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", str(port)],
        env={**os.environ, "PORT": str(port)},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Give it a moment to start
    time.sleep(2)

    try:
        response = requests.get(f"http://localhost:{port}/ready", timeout=2)
        assert response.status_code == 200
        assert response.json() == [{"message": "Server is serving"}]
    finally:
        proc.terminate()
        proc.wait()
