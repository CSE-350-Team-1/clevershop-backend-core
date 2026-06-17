Testing Documentation – CleverShop Backend
This document explains all what the testing encompasses, including:

Unit tests – verify individual components in isolation.

Integration tests – verify the interaction between components and the system as a whole.

The test suite validates core functionality: health checks, request correlation (correlation‑ID handling), error logging, and middleware exemption.

📁 Folder Structure
test/
├── config_for_tests.py              # Shared configurations for all tests (client, temp_log_path, test routes)
├── unit_testing.py          # All unit tests (TC‑01 to TC‑06, TC‑08)
├── integration_test.py      # All integration tests (TC‑07 + container/environment tests)
└── testingDocs.md           # This file – testing documentation


🧪 Test Suite Overview
Test ID	Title	What It Verifies
TC‑01	Health Check Success	/ready returns 200 OK with the correct JSON payload.
TC‑02	Health Check Exemption	Confirms /ready is in EXEMPT_ROUTES – the error middleware is bypassed.
TC‑03	Missing Correlation ID	A valid UUIDv4 is auto‑generated when no correlation_id header is sent.
TC‑04	Provided (Valid) Correlation ID	The exact UUID header is used in the error log when a valid UUID is provided.
TC‑04b	Invalid Correlation ID	Malformed UUIDs are discarded and replaced with a valid one.
TC‑05	Unhandled Exception Logging	Error logs contain all required fields (type, correlation_id, timestamps, message).
TC‑06	Log File Creation	The logs/ folder and error-log.jsonl are created automatically on the first error.
TC‑07	Port Binding (integration)	The container listens on the PORT environment variable.
TC‑08	Middleware Exemption (documentation)	Confirms /ready bypasses middleware – proven by TC‑02.

🔧 Prerequisites
Python 3.8+ (or 3.12+ as used in CI)

pip (or uv for faster installs)

All dependencies listed below

Install the required packages:
Using pip:

bash
pip install fastapi uvicorn pytest httpx
Using uv (faster):

bash
uv pip install fastapi uvicorn pytest httpx
▶️ Running the Tests
Navigate to the project root (where the test/ folder resides) and run:

Run all tests:
bash
python -m pytest test/ -v
Run only unit tests:
bash
python -m pytest test/unit_testing.py -v
Run only integration tests:
bash
python -m pytest test/integration_test.py -v
Less verbose output:
bash
python -m pytest test/


Column	Description
Test ID	Unique identifier (e.g., TC‑01)
Test Title	Brief description of the test
Steps (brief)	High‑level steps to execute
Expected Outcome	What should happen if the test passes
Actual Result	What actually happened during execution
Status	Pass / Fail / Blocked
Tester	Name of the person who ran the test
Date	Date of execution
📎 Link to the shared spreadsheet: [Insert URL here]

✍️ Writing New Tests

# ***REMEMBER: You will need to write tests according to the feature you add.***

Place all test files inside the test/ directory.

Use the existing conftest.py for shared fixtures (client, temp_log_path, clear_log, etc.).

Each test function should be commented with its TC‑ID and a one‑line description of its purpose (as shown in unit_testing.py).

If your feature requires a test‑only route (like /raise-error), add it via a fixture in conftest.py – do not add test routes to production code.

CI Integration
The test suite is designed to run in a CI pipeline (e.g., GitHub Actions, GitLab CI, Jenkins). The build step should:

Install dependencies (pip install -r requirements.txt or the packages listed above).

Run pytest with the appropriate flags.

A green status confirms the backend is ready for deployment.

Additional Resources
Source code: src/main.py, src/middleware/ – the components being tested.

Error logging: defined in src/middleware/error_middleware.py.
