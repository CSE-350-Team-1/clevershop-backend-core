import os
import uvicorn
import urllib.parse

from src.errors.errors import InitError, ShutDownError
from src.main import app
import src.core as core


if __name__ == "__main__":
    try:
        port = int(os.getenv("PORT", "8000"))

        dbhost = os.getenv("DBHOST", "")
        dbname = os.getenv("DBNAME", "")
        dbuser_raw = os.getenv("DBUSER", "") or ""
        dbuser = urllib.parse.quote(dbuser_raw)
        password = os.getenv("DBPASSWORD", "") or ""
        db_port = int(os.getenv("DBPORT", "5432"))
        sslmode = os.getenv("SSLMODE", "require")

        db_uri = f"host={dbhost} dbname={dbname} user={dbuser} password={password} port={db_port} sslmode={sslmode}"
        core.conn_str = db_uri
        core.init_cursor()

        uvicorn.run(app, host="0.0.0.0", port=port)

    except Exception as e:
        raise InitError(f"Server initialization failed: {e}") from e
    finally:
        try:
            core.kill_db_connection()
        except Exception as e:
            raise ShutDownError(f"Server shutdown error: {e}") from e
