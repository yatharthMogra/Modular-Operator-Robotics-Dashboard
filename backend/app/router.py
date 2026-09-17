from __future__ import annotations

from app.managers.events import EventLog
from app.protocol import CommandAck
from app.simulator.engine import Simulator


def handle_command(sim: Simulator, events: EventLog, request_id: str, tile_id: str, action: str, payload: dict) -> tuple[dict, list[dict]]:
    result = sim.apply_command(tile_id, action, payload)
    ack = CommandAck(
        request_id=request_id,
        status=result["status"],
        state=result.get("state"),
        reason=result.get("reason"),
    )
    if ack.status == "accepted":
        ev = events.emit(
            f"Tile {tile_id} {action} command",
            tile_id=tile_id,
            request_id=request_id,
        )
    else:
        ev = events.emit(
            f"Tile {tile_id} {action} rejected ({ack.reason})",
            level="warn",
            tile_id=tile_id,
            request_id=request_id,
        )
    return ack.model_dump(), [ev]


def handle_configure(sim: Simulator, events: EventLog, request_id: str, start: tuple[int, int], end: tuple[int, int]) -> tuple[dict, list[dict]]:
    result = sim.configure(start, end)
    ack = CommandAck(
        request_id=request_id,
        status=result["status"],
        state=result.get("state"),
        reason=result.get("reason"),
    )
    emitted: list[dict] = []
    if ack.status == "accepted":
        emitted.append(events.emit(f"configuration requested {start} → {end}", request_id=request_id))
        emitted.append(events.emit("tiles assigned to conveyor slots"))
    else:
        emitted.append(
            events.emit(
                f"configuration rejected ({ack.reason})",
                level="warn",
                request_id=request_id,
            )
        )
    return ack.model_dump(), emitted
