import uuid
import time


class RequestContext:
    def __init__(self, correlation_id = ""):
        try:
            val = uuid.UUID(correlation_id, version=4)
            self.correlation_id = correlation_id
        except Exception:
            self.correlation_id = str(uuid.uuid4())

        self.time = time.time()
