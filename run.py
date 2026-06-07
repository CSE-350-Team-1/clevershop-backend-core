import os
import uvicorn

from src.errors.errors import InitError
from src.main import app

if __name__ == "__main__":

    try:
        port = int(os.getenv("PORT", "8000"))
        uvicorn.run(app, host="0.0.0.0", port=port)

    except Exception as e:
        raise InitError(f"Server initialization failed: {str(e)}") from e
