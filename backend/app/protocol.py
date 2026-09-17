from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel


class CommandAck(BaseModel):
    type: Literal["command_ack"] = "command_ack"
    request_id: str
    status: Literal["accepted", "rejected"]
    state: Optional[str] = None
    reason: Optional[str] = None


class EventMessage(BaseModel):
    type: Literal["event"] = "event"
    t: float
    level: Literal["info", "warn", "error"]
    tile_id: Optional[str] = None
    message: str
    request_id: Optional[str] = None


def snapshot_envelope(t: float, tick_hz: float, tiles: List[Dict[str, Any]], world: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "type": "snapshot",
        "t": t,
        "tick_hz": tick_hz,
        "tiles": tiles,
        "world": world,
    }
