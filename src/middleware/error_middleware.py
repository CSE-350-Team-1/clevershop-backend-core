import json
import traceback
from pathlib import Path
import time
from datetime import datetime

LOG_PATH = Path("logs/error-log.jsonl")


class Error:
    def __init__(self, request_context, error_message: str):
        self.correlation_id = request_context.correlation_id
        self.request_time = request_context.time
        self.error_time = time.time()
        self.error_message = error_message

    def log_error(self):
        """Log error to errors.json"""

        error_obj = {
            "type": "error",
            "correlation_id": str(self.correlation_id),
            "request_time": datetime.fromtimestamp(self.request_time).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            ),
            "error_time": datetime.fromtimestamp(self.error_time).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            ),
            "message": self.error_message,
        }

        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(error_obj))
            f.write("\n")
