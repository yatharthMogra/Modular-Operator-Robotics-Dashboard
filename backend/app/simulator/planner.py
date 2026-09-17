from __future__ import annotations

import math
from collections import deque
from typing import Iterable

from app.config import GRID_COLS, GRID_ROWS, TILE_SIZE
from app.simulator.sensors import aabb_overlap, tile_aabb
from app.simulator.world import OBSTACLES, obstacle_aabb


def cell_center(col: int, row: int) -> tuple[float, float]:
    return (col + 0.5) * TILE_SIZE, (row + 0.5) * TILE_SIZE


def cell_blocked(col: int, row: int) -> bool:
    if not (0 <= col < GRID_COLS and 0 <= row < GRID_ROWS):
        return True
    cx, cy = cell_center(col, row)
    cell = tile_aabb(cx, cy)
    return any(aabb_overlap(cell, obstacle_aabb(obs)) for obs in OBSTACLES)


def bfs_path(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]] | None:
    if cell_blocked(*start) or cell_blocked(*end):
        return None
    q: deque[tuple[int, int]] = deque([start])
    prev: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    while q:
        cur = q.popleft()
        if cur == end:
            break
        c, r = cur
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (c + dc, r + dr)
            if nxt in prev or cell_blocked(*nxt):
                continue
            prev[nxt] = cur
            q.append(nxt)
    if end not in prev:
        return None
    path = []
    node: tuple[int, int] | None = end
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    return path


def slot_heading(path: list[tuple[int, int]], i: int) -> float:
    if len(path) == 1:
        return 0.0
    if i < len(path) - 1:
        a, b = path[i], path[i + 1]
    else:
        a, b = path[i - 1], path[i]
    ax, ay = cell_center(*a)
    bx, by = cell_center(*b)
    return math.atan2(by - ay, bx - ax)


def greedy_assign(tiles: Iterable, slots: list[tuple[float, float, float]]) -> list[tuple[object, tuple[float, float, float]]]:
    remaining = list(tiles)
    assigned = []
    for slot in slots:
        if not remaining:
            break
        sx, sy, _ = slot
        best = min(remaining, key=lambda t: (t.x - sx) ** 2 + (t.y - sy) ** 2)
        remaining.remove(best)
        assigned.append((best, slot))
    return assigned


def plan_conveyor(start: tuple[int, int], end: tuple[int, int], tiles: list) -> list[tuple[object, tuple[float, float, float]]] | None:
    path = bfs_path(start, end)
    if not path:
        return None
    path = path[: len(tiles)]
    slots = []
    for i, cell in enumerate(path):
        x, y = cell_center(*cell)
        slots.append((x, y, slot_heading(path, i)))
    return greedy_assign(tiles, slots)
