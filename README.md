# clevershop-backend-process-template

## Summary

This is a template backend process for the CleverShop project. It provides a foundational structure for building containerized backend services with error handling, middleware support, and extensible tool integration.

## Repository Structure

```
clevershop-backend-process-template/
├── src/                           # Main source code
│   ├── __init__.py
│   ├── main.py                    # Entry point for the application
│   ├── core.py                    # Core business logic (empty)
│   ├── errors/                    # Error handling module
│   │   ├── __init__.py
│   │   └── errors.py              # Custom error definitions
│   ├── middleware/                # Middleware components
│   │   ├── __init__.py
│   │   ├── authorization_middleware.py
│   │   ├── context_middleware.py  # Request context management middleware
│   │   └── error_middleware.py    # Error handling middleware
│   ├── rbac/                      # RBAC helpers
│   │   ├── __init__.py
│   │   └── rbac.py
│   └── tools/                     # Extension point for additional business utilities
│       ├── __init__.py
│       └── account.py
├── logs/                          # Server logs (automatically generated)
│   └── error-log.jsonl
├── test/                          # Test suite
├── run.py                         # Application runner script
├── Dockerfile                     # Container configuration
├── docker-compose.yml             # Compose configuration
├── requirements.txt               # Python dependencies
├── AGENTS.md                      # Agent documentation
├── .gitignore                     # Ignored files and folders
└── README.md                       # This file
```

## Build and Run Instructions

### Prerequisites

- Docker installed on your system

### Building the Container

To build the Docker image, run:

```bash
docker build -t clevershop-backend .
```

This command will:
- Read the Dockerfile configuration
- Install all dependencies
- Create a Docker image tagged as `clevershop-backend`

> Container must build successfully to pass CI checks

### Docker Compose and .env

Sensitive configuration (DB credentials, passwords, etc.) should not be committed to the repository. Use an `.env` file (copy from `.env.example`) or CI/CD/secret manager to inject secrets at runtime.

Examples:

- Using an env file with `docker run`:

```bash
docker run --env-file .env -v "$(pwd)/logs:/app/logs" -p 8000:8000 clevershop-backend

```

- Passing explicit environment variables (not recommended for secrets):

```bash
docker run -e DBHOST=yourhost -e DBNAME=yourdb -e DBUSER=youruser -e DBPASSWORD=yourpass -v "$(pwd)/logs:/app/logs" -p 8000:8000 clevershop-backend
```

- Using `docker compose` (reads `.env` automatically when `env_file` is configured):

```bash
docker compose up --build
```

Notes:
- If you use `docker compose`, the provided `docker-compose.yml` already mounts `./logs` to `/app/logs`.

Notes:
- Copy `.env.example` to `.env` and fill real values locally. Do NOT commit `.env`.
- For production, prefer using a secrets manager, Kubernetes Secrets, or your CI/CD provider's secret store.

## Repository rules

### Update model
- Pull requests must adhere to the following requirements before approval:
    - At least 1 approving review
    - CI checks passed; run the following command for formatting verification:
        - `black .`
        > Run `pip install black` if not installed already

### Branching rules
- The use of feature branches is mandatory.
- All branches must have main as the origin.