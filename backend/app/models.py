from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, Field

TileState = Literal["IDLE", "MOVING", "ROTATING", "WARNING", "STOP", "OFFLINE"]
CommandAction = Literal["MOVE", "ROTATE", "STOP", "RESET"]


class Proximity(BaseModel):
    front: float
    left: float
    right: float
    rear: float


class LidarHit(BaseModel):
    angle: float  # offset from heading, radians
    range: float


class PoseTarget(BaseModel):
    x: float
    y: float
    theta: Optional[float] = None


class TileSnapshot(BaseModel):
    id: str
    connected: bool
    state: TileState
    x: float
    y: float
    theta: float
    vx: float
    vy: float
    omega: float
    battery: float
    proximity: Proximity
    lidar: List[LidarHit]
    target: Optional[PoseTarget] = None


class Obstacle(BaseModel):
    x: float
    y: float
    w: float
    h: float


class WorldSnapshot(BaseModel):
    width: float
    height: float
    tile_size: float
    obstacles: List[Obstacle]


class CommandIn(BaseModel):
    type: Literal["command"] = "command"
    request_id: str
    tile_id: str
    action: CommandAction
    payload: Dict[str, Any] = Field(default_factory=dict)


class ConfigureIn(BaseModel):
    type: Literal["configure"] = "configure"
    request_id: str
    start: Tuple[int, int]
    end: Tuple[int, int]
