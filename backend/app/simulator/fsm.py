from __future__ import annotations

from app.config import STOP_M, WARN_M

STATES = ("IDLE", "MOVING", "ROTATING", "WARNING", "STOP", "OFFLINE")


def step_fsm(
    *,
    state: str,
    front: float,
    has_move: bool,
    has_rotate: bool,
    motion_done: bool,
    emergency: bool,
) -> tuple[str, bool, str | None]:
    """Pure FSM tick. Returns (state, emergency, event_message)."""
    if state == "OFFLINE":
        return state, emergency, None

    if state == "STOP" and emergency:
        return state, True, None

    if front < STOP_M and state in ("MOVING", "ROTATING", "WARNING", "IDLE"):
        if has_move or has_rotate or state in ("MOVING", "ROTATING", "WARNING"):
            return "STOP", True, "emergency stop"

    if state in ("MOVING", "ROTATING") and front < WARN_M:
        return "WARNING", False, "proximity warning"

    if state == "WARNING":
        if front < WARN_M:
            return "WARNING", False, None
        if has_rotate and not motion_done:
            return "ROTATING", False, "proximity clear"
        if has_move and not motion_done:
            return "MOVING", False, "proximity clear"
        return "IDLE", False, "proximity clear"

    if has_rotate and not motion_done:
        if state != "ROTATING":
            return "ROTATING", False, "ROTATING"
        return "ROTATING", False, None

    if has_move and not motion_done:
        if state != "MOVING":
            return "MOVING", False, "MOVING"
        return "MOVING", False, None

    if motion_done and state in ("MOVING", "ROTATING"):
        return "IDLE", False, None

    if state == "STOP" and not emergency:
        if has_move:
            return "MOVING", False, "MOVING"
        if has_rotate:
            return "ROTATING", False, "ROTATING"
        return "STOP", False, None

    return state, emergency, None
