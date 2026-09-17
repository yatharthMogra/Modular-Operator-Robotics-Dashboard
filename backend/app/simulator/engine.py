from __future__ import annotations

import time
from typing import Any

from app.config import DT, TICK_HZ
from app.protocol import snapshot_envelope
from app.simulator.planner import plan_conveyor
from app.simulator.tile import Tile, spawn_tiles
from app.simulator.world import world_snapshot


class Simulator:
    def __init__(self) -> None:
        self.tiles: dict[str, Tile] = spawn_tiles()
        self._formation_complete_sent = True
        others = self.all_tiles()
        for tile in others:
            tile.sense(others)

    def all_tiles(self) -> list[Tile]:
        return list(self.tiles.values())

    def step(self, dt: float = DT) -> list[dict[str, Any]]:
        others = self.all_tiles()
        for tile in others:
            tile.integrate(dt, others)
        for tile in others:
            tile.sense(others)
        events: list[dict[str, Any]] = []
        for tile in others:
            events.extend(tile.update_fsm())
        if not self._formation_complete_sent and all(
            t._goto is None and t.state not in ("MOVING", "ROTATING") for t in others
        ):
            self._formation_complete_sent = True
            events.append({"level": "info", "tile_id": None, "message": "formation complete"})
        return events

    def snapshot_message(self) -> dict[str, Any]:
        return snapshot_envelope(
            t=time.time(),
            tick_hz=float(TICK_HZ),
            tiles=[t.to_dict() for t in self.all_tiles()],
            world=world_snapshot().model_dump(),
        )

    def apply_command(self, tile_id: str, action: str, payload: dict) -> dict[str, Any]:
        tile = self.tiles.get(tile_id)
        if tile is None:
            return {"status": "rejected", "reason": "unknown_tile", "state": None}
        if action == "RESET":
            tile.reset()
            return {"status": "accepted", "reason": None, "state": tile.state}
        if not tile.connected and action != "RESET":
            return {"status": "rejected", "reason": "offline", "state": tile.state}

        if action == "MOVE":
            err = tile.apply_move(float(payload.get("fx", 0)), float(payload.get("fy", 0)))
            if err:
                return {"status": "rejected", "reason": err, "state": tile.state}
            return {"status": "accepted", "reason": None, "state": "MOVING"}
        if action == "ROTATE":
            err = tile.apply_rotate(float(payload.get("delta_deg", 90)))
            if err:
                return {"status": "rejected", "reason": err, "state": tile.state}
            return {"status": "accepted", "reason": None, "state": "ROTATING"}
        if action == "STOP":
            tile.apply_stop(emergency=False)
            return {"status": "accepted", "reason": None, "state": "STOP"}
        return {"status": "rejected", "reason": "bad_payload", "state": tile.state}

    def configure(self, start: tuple[int, int], end: tuple[int, int]) -> dict[str, Any]:
        live = [t for t in self.all_tiles() if t.connected]
        planned = plan_conveyor(start, end, live)
        if not planned:
            return {"status": "rejected", "reason": "no_path", "state": None}
        for tile, (x, y, th) in planned:
            tile.apply_goto(x, y, th)
        self._formation_complete_sent = False
        return {"status": "accepted", "reason": None, "state": "MOVING"}
