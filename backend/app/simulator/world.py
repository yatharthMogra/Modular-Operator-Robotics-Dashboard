from __future__ import annotations

from app.config import TILE_SIZE, WORLD_HEIGHT, WORLD_WIDTH
from app.models import Obstacle, WorldSnapshot

# Keep the middle corridor (around y=3.6, row 4) clear for conveyor (2,4)→(9,4).
OBSTACLES: list[Obstacle] = [
    Obstacle(x=5.0, y=0.35, w=1.6, h=0.85),
    Obstacle(x=1.3, y=6.15, w=2.0, h=1.05),
    Obstacle(x=9.4, y=6.3, w=1.5, h=0.9),
]

# Scattered initial layout (not a line).
SPAWN: list[tuple[str, float, float, float]] = [
    ("01", 2.0, 3.6, 0.0),
    ("02", 6.0, 1.75, 0.0),
    ("03", 6.0, 3.6, 0.0),
    ("04", 10.0, 3.6, 0.0),
    ("05", 6.0, 5.4, 0.0),
    ("06", 4.2, 6.6, 0.0),
    ("07", 7.6, 6.5, 0.0),
    ("08", 10.4, 5.2, 0.0),
]


def world_snapshot() -> WorldSnapshot:
    return WorldSnapshot(
        width=WORLD_WIDTH,
        height=WORLD_HEIGHT,
        tile_size=TILE_SIZE,
        obstacles=list(OBSTACLES),
    )


def obstacle_aabb(obs: Obstacle) -> tuple[float, float, float, float]:
    return obs.x, obs.y, obs.x + obs.w, obs.y + obs.h
