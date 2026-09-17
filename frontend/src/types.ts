export type ConnStatus = "CONNECTED" | "RECONNECTING" | "OFFLINE";

export type TileState = "IDLE" | "MOVING" | "ROTATING" | "WARNING" | "STOP" | "OFFLINE";

export interface Proximity {
  front: number;
  left: number;
  right: number;
  rear: number;
}

export interface LidarHit {
  angle: number;
  range: number;
}

export interface Tile {
  id: string;
  connected: boolean;
  state: TileState;
  x: number;
  y: number;
  theta: number;
  vx: number;
  vy: number;
  omega: number;
  battery: number;
  proximity: Proximity;
  lidar: LidarHit[];
  target: { x: number; y: number; theta: number | null } | null;
}

export interface Obstacle {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface World {
  width: number;
  height: number;
  tile_size: number;
  obstacles: Obstacle[];
}

export interface Snapshot {
  type: "snapshot";
  t: number;
  tick_hz: number;
  tiles: Tile[];
  world: World;
}

export interface EventMsg {
  type: "event";
  t: number;
  level: "info" | "warn" | "error";
  tile_id: string | null;
  message: string;
  request_id?: string | null;
}

export interface CommandAck {
  type: "command_ack";
  request_id: string;
  status: "accepted" | "rejected";
  state: string | null;
  reason: string | null;
}

export type WsInbound = Snapshot | EventMsg | CommandAck;
