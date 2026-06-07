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
│   │   ├── context_middleware.py  # Request context management middleware
│   │   └── error_middleware.py    # Error handling middleware
│   └── tools/                     # Extension point for additional business utilities (empty)
├── logs/                          # Server logs (automatically generated)
├── test/                          # Test suite (empty)
├── run.py                         # Application runner script
├── Dockerfile                     # Container configuration
├── AGENTS.md                      # Agent documentation
├── .gitignore                     # Ignored files and folders
└──README.md                       # This file
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

### Running the Container

To run the container, execute:

```bash
docker run -e PORT=8000 -p 8000:8000 clevershop-backend
```

Optionally, mount a local logs directory so container logs persist outside the container:

```bash
docker run -e PORT=8000 -p 8000:8000 -v $(pwd)/logs:/app/logs clevershop-backend
```

When mounting logs from multiple containers, avoid file naming conflicts by using separate host directories or distinct file names for each container.
> `LOG PATH` is specified in `error_middleware.py`

This command will:
- Start a new container from the `clevershop-backend` image
- Set the `PORT` environment variable to `8000`
- Map port `8000` from the container to port `8000` on your local machine
- Mount a local logs directory
- Make the service accessible at `http://localhost:8000`

> PORT values are adjustable so long as all three values match

### Environment Variables

- `PORT`: The port on which the backend service will listen (default: 8000)

## Repository rules

### Update model
- Pull requests must adhere to the following requirements before approval:
    - At least 1 approving review
    - CI checks passed; run the following commands for verification:
        - `black .`
        - `bandit .`
        - `mypy .` (not enforced)
        > Install `black`, `bandit`, and `mypy` using pip
- All files and folders beside `.github/`, `README.md`, `AGENTS.md`, `.gitkeep`, `Dockerfile`, , `__init__.py`, and `.gitignore` must adhere to kebab-case.

### Branching rules
- The use of feature branches is mandatory.
- All branches must have main as the origin.