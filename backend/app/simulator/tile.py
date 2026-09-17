from __future__ import annotations

import math
from typing import Any

from app.config import (
    BATTERY_DRAIN_PER_SEC,
    GOTO_ARRIVE_M,
    HEADING_ARRIVE_RAD,
    LOW_BATTERY,
    MAX_OMEGA,
    MAX_SPEED,
)
from app.simulator.fsm import step_fsm
from app.simulator.sensors import aabb_overlap, in_bounds, tile_aabb, update_sensors
from app.simulator.world import OBSTACLES, SPAWN, obstacle_aabb


def _angle_diff(current: float, target: float) -> float:
    return (target - current + math.pi) % (2 * math.pi) - math.pi


def _norm2(x: float, y: float) -> tuple[float, float]:
    mag = math.hypot(x, y)
    if mag < 1e-9:
        return 0.0, 0.0
    return x / mag, y / mag


class Tile:
    def __init__(self, id: str, x: float, y: float, theta: float):
        self.id = id
        self.x = x
        self.y = y
        self.theta = theta
        self.spawn = (x, y, theta)
        self.vx = 0.0
        self.vy = 0.0
        self.omega = 0.0
        self.battery = 100.0
        self.connected = True
        self.state = "IDLE"
        self.proximity = {"front": 4.0, "left": 4.0, "right": 4.0, "rear": 4.0}
        self.lidar: list[dict[str, float]] = []
        self.emergency = False
        self.low_battery_sent = False

        self._fx = 0.0
        self._fy = 0.0
        self._heading_target: float | None = None
        self._goto: tuple[float, float, float] | None = None

    @property
    def target(self) -> dict[str, float] | None:
        if self._goto:
            return {"x": self._goto[0], "y": self._goto[1], "theta": self._goto[2]}
        if self._heading_target is not None:
            return {"x": self.x, "y": self.y, "theta": self._heading_target}
        return None

    def reset(self) -> None:
        self.x, self.y, self.theta = self.spawn
        self.vx = self.vy = self.omega = 0.0
        self.battery = 100.0
        self.connected = True
        self.state = "IDLE"
        self.emergency = False
        self.low_battery_sent = False
        self._fx = self._fy = 0.0
        self._heading_target = None
        self._goto = None

    def set_offline(self, offline: bool) -> None:
        self.connected = not offline
        if offline:
            self.vx = self.vy = self.omega = 0.0
            self.state = "OFFLINE"
            self._fx = self._fy = 0.0
            self._heading_target = None
            self._goto = None
        else:
            self.state = "IDLE"

    def apply_move(self, fx: float, fy: float) -> str | None:
        if self.emergency:
            return "unsafe_state"
        if not self.connected:
            return "offline"
        self._fx, self._fy = _norm2(fx, fy)
        self._heading_target = None
        self._goto = None
        if self.state != "WARNING":
            self.state = "MOVING"
        return None

    def apply_rotate(self, delta_deg: float) -> str | None:
        if self.emergency:
            return "unsafe_state"
        if not self.connected:
            return "offline"
        self._fx = self._fy = 0.0
        self._goto = None
        self._heading_target = self.theta + math.radians(delta_deg)
        if self.state != "WARNING":
            self.state = "ROTATING"
        return None

    def apply_stop(self, *, emergency: bool = False) -> None:
        self._fx = self._fy = 0.0
        self._heading_target = None
        self._goto = None
        self.vx = self.vy = self.omega = 0.0
        self.emergency = emergency
        self.state = "STOP"

    def apply_goto(self, x: float, y: float, theta: float) -> None:
        self.emergency = False
        self._fx = self._fy = 0.0
        self._heading_target = None
        self._goto = (x, y, theta)
        self.state = "MOVING"

    def _body_world_vel(self) -> tuple[float, float]:
        fx, fy = self._fx, self._fy
        if fx == 0 and fy == 0:
            return 0.0, 0.0
        # fy = forward along heading, fx = strafe right
        c, s = math.cos(self.theta), math.sin(self.theta)
        # fy = forward (heading), fx = strafe right (heading + 90°) in y-down frame
        vx = (fy * c - fx * s) * MAX_SPEED
        vy = (fy * s + fx * c) * MAX_SPEED
        return vx, vy

    def integrate(self, dt: float, others: list[Tile]) -> None:
        if not self.connected or self.state == "OFFLINE":
            self.vx = self.vy = self.omega = 0.0
            return

        prev = (self.x, self.y, self.theta)
        self.vx = self.vy = self.omega = 0.0

        if self._goto is not None:
            gx, gy, gth = self._goto
            dx, dy = gx - self.x, gy - self.y
            dist = math.hypot(dx, dy)
            if dist > GOTO_ARRIVE_M:
                self.vx = MAX_SPEED * dx / dist
                self.vy = MAX_SPEED * dy / dist
            else:
                self.x, self.y = gx, gy
                err = _angle_diff(self.theta, gth)
                if abs(err) > HEADING_ARRIVE_RAD:
                    self.omega = MAX_OMEGA if err > 0 else -MAX_OMEGA
                    step = self.omega * dt
                    if abs(step) > abs(err):
                        self.theta = gth
                        self.omega = 0.0
                        self._goto = None
                    else:
                        self.theta += step
                else:
                    self.theta = gth
                    self._goto = None
        elif self._heading_target is not None:
            err = _angle_diff(self.theta, self._heading_target)
            if abs(err) <= HEADING_ARRIVE_RAD:
                self.theta = self._heading_target
                self._heading_target = None
            else:
                self.omega = MAX_OMEGA if err > 0 else -MAX_OMEGA
                step = self.omega * dt
                if abs(step) > abs(err):
                    self.theta = self._heading_target
                    self.omega = 0.0
                    self._heading_target = None
                else:
                    self.theta += step
        else:
            self.vx, self.vy = self._body_world_vel()

        if self.emergency:
            self.vx = self.vy = self.omega = 0.0

        self.x += self.vx * dt
        self.y += self.vy * dt

        if not in_bounds(self.x, self.y) or self._collides(others):
            self.x, self.y, self.theta = prev
            self.vx = self.vy = self.omega = 0.0

        moving = abs(self.vx) + abs(self.vy) + abs(self.omega) > 1e-6
        if moving:
            self.battery = max(0.0, self.battery - BATTERY_DRAIN_PER_SEC * dt)

    def _collides(self, others: list[Tile]) -> bool:
        me = tile_aabb(self.x, self.y)
        for obs in OBSTACLES:
            if aabb_overlap(me, obstacle_aabb(obs)):
                return True
        for o in others:
            if o.id == self.id or not o.connected:
                continue
            if aabb_overlap(me, tile_aabb(o.x, o.y)):
                return True
        return False

    def sense(self, others: list[Tile]) -> None:
        update_sensors(self, others)

    def update_fsm(self) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        if not self.connected:
            self.state = "OFFLINE"
            return events

        has_move = (self._fx != 0 or self._fy != 0) or (
            self._goto is not None
            and math.hypot(self._goto[0] - self.x, self._goto[1] - self.y) > GOTO_ARRIVE_M
        )
        has_rotate = self._heading_target is not None or (
            self._goto is not None
            and math.hypot(self._goto[0] - self.x, self._goto[1] - self.y) <= GOTO_ARRIVE_M
        )
        motion_done = (
            self._fx == 0
            and self._fy == 0
            and self._heading_target is None
            and self._goto is None
        )
        new_state, emergency, msg = step_fsm(
            state=self.state,
            front=self.proximity["front"],
            has_move=has_move,
            has_rotate=has_rotate,
            motion_done=motion_done,
            emergency=self.emergency,
        )
        if emergency and not self.emergency:
            self.apply_stop(emergency=True)
            new_state = "STOP"
        self.emergency = emergency
        if new_state != self.state and msg:
            level = "error" if new_state == "STOP" and emergency else "warn" if new_state == "WARNING" else "info"
            events.append({"level": level, "tile_id": self.id, "message": f"Tile {self.id} {msg}"})
        self.state = new_state
        if emergency:
            self.state = "STOP"

        if self.battery <= LOW_BATTERY and not self.low_battery_sent:
            self.low_battery_sent = True
            events.append({"level": "warn", "tile_id": self.id, "message": f"Tile {self.id} battery low"})
        return events

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "connected": self.connected,
            "state": self.state,
            "x": round(self.x, 4),
            "y": round(self.y, 4),
            "theta": round(self.theta, 4),
            "vx": round(self.vx, 4),
            "vy": round(self.vy, 4),
            "omega": round(self.omega, 4),
            "battery": round(self.battery, 2),
            "proximity": {k: round(v, 3) for k, v in self.proximity.items()},
            "lidar": [{"angle": round(h["angle"], 4), "range": round(h["range"], 3)} for h in self.lidar],
            "target": self.target,
        }


def spawn_tiles() -> dict[str, Tile]:
    return {tid: Tile(tid, x, y, th) for tid, x, y, th in SPAWN}
