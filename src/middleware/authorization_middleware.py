import uuid
import time
import asyncio


class Session:
    def __init__(self, username: str):
        self.username = username
        self.session_id = str(uuid.uuid4())
        self.session_init_time: float = time.time()


_sessions: dict[str, Session] = {}


async def create_session(username: str) -> str:
    new_session = Session(username)
    new_session_id = new_session.session_id
    _sessions[new_session_id] = new_session
    return new_session_id


async def end_session(username: str):
    expired_keys = [sid for sid, session in _sessions.items() if session.username == username]
    for sid in expired_keys:
        _sessions.pop(sid, None)


async def validate_token(access_token: str) -> tuple[bool, str]:
    expired_sessions = [
        sid
        for sid, session in _sessions.items()
        if time.time() - session.session_init_time > 3600
    ]
    for sid in expired_sessions:
        _sessions.pop(sid, None)

    session = _sessions.get(access_token)
    if session is None:
        return (False, "")

    return (True, session.username)
