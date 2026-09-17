from __future__ import annotations

import time
from collections import deque

from app.config import EVENT_BUFFER
from app.protocol import EventMessage


class EventLog:
    def __init__(self, maxlen: int = EVENT_BUFFER) -> None:
        self._buf: deque[dict] = deque(maxlen=maxlen)

    def emit(
        self,
        message: str,
        *,
        level: str = "info",
        tile_id: str | None = None,
        t: float | None = None,
        request_id: str | None = None,
    ) -> dict:
        ev = EventMessage(
            t=t if t is not None else time.time(),
            level=level,  # type: ignore[arg-type]
            tile_id=tile_id,
            message=message,
            request_id=request_id,
        ).model_dump()
        self._buf.appendleft(ev)
        return ev

    def list(self, limit: int = 100) -> list[dict]:
        return list(self._buf)[:limit]
