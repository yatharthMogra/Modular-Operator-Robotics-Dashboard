from __future__ import annotations

import math

import numpy as np

from app.config import LIDAR_MAX, LIDAR_RAYS, PROXIMITY_MAX, TILE_SIZE, WORLD_HEIGHT, WORLD_WIDTH
from app.simulator.world import OBSTACLES, obstacle_aabb


def ray_aabb(
    ox: float,
    oy: float,
    dx: float,
    dy: float,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
) -> float | None:
    """Slab-method ray vs AABB. dx,dy unit. Returns t >= 0 or None."""
    tmin = 0.0
    tmax = 1e9
    for origin, direction, lo, hi in ((ox, dx, x0, x1), (oy, dy, y0, y1)):
        if abs(direction) < 1e-12:
            if origin < lo or origin > hi:
                return None
            continue
        t1 = (lo - origin) / direction
        t2 = (hi - origin) / direction
        if t1 > t2:
            t1, t2 = t2, t1
        tmin = max(tmin, t1)
        tmax = min(tmax, t2)
        if tmax < tmin:
            return None
    if tmin >= 0:
        return tmin
    return None


def _rects_for(tile, tiles) -> list[tuple[float, float, float, float]]:
    rects: list[tuple[float, float, float, float]] = []
    # Arena walls as four thin AABBs just outside, plus interior obstacles.
    wall = 0.05
    rects.extend(
        [
            (-wall, -wall, WORLD_WIDTH + wall, 0.0),
            (-wall, WORLD_HEIGHT, WORLD_WIDTH + wall, WORLD_HEIGHT + wall),
            (-wall, 0.0, 0.0, WORLD_HEIGHT),
            (WORLD_WIDTH, 0.0, WORLD_WIDTH + wall, WORLD_HEIGHT),
        ]
    )
    for obs in OBSTACLES:
        rects.append(obstacle_aabb(obs))
    half = TILE_SIZE / 2
    for other in tiles:
        if other.id == tile.id or not other.connected:
            continue
        rects.append((other.x - half, other.y - half, other.x + half, other.y + half))
    return rects


def cast(ox: float, oy: float, angle: float, rects, max_range: float) -> float:
    dx = math.cos(angle)
    dy = math.sin(angle)
    best = max_range
    for x0, y0, x1, y1 in rects:
        t = ray_aabb(ox, oy, dx, dy, x0, y0, x1, y1)
        if t is not None and 1e-4 < t < best:
            best = t
    return best


def update_sensors(tile, tiles) -> None:
    rects = _rects_for(tile, tiles)
    offsets = np.linspace(0.0, 2 * math.pi, LIDAR_RAYS, endpoint=False)
    lidar = []
    for off in offsets:
        rng = float(cast(tile.x, tile.y, tile.theta + float(off), rects, LIDAR_MAX))
        lidar.append({"angle": float(off), "range": rng})
    tile.lidar = lidar
    tile.proximity = {
        "front": float(cast(tile.x, tile.y, tile.theta, rects, PROXIMITY_MAX)),
        "right": float(cast(tile.x, tile.y, tile.theta + math.pi / 2, rects, PROXIMITY_MAX)),
        "rear": float(cast(tile.x, tile.y, tile.theta + math.pi, rects, PROXIMITY_MAX)),
        "left": float(cast(tile.x, tile.y, tile.theta - math.pi / 2, rects, PROXIMITY_MAX)),
    }


def tile_aabb(x: float, y: float) -> tuple[float, float, float, float]:
    h = TILE_SIZE / 2
    return x - h, y - h, x + h, y + h


def aabb_overlap(a, b) -> bool:
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def in_bounds(x: float, y: float) -> bool:
    h = TILE_SIZE / 2
    return h <= x <= WORLD_WIDTH - h and h <= y <= WORLD_HEIGHT - h
