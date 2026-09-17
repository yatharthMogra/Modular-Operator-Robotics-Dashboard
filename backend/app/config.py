"""World and plant constants.

Coordinate frame: origin at the top-left of the arena, +x right, +y down
(SVG-aligned). Heading 0 faces +x.
"""

TICK_HZ = 20
DT = 1.0 / TICK_HZ

WORLD_WIDTH = 12.0
WORLD_HEIGHT = 8.0
TILE_SIZE = 0.8
N_TILES = 8

MAX_SPEED = 0.55  # m/s
MAX_OMEGA = 1.4  # rad/s

LIDAR_RAYS = 72
LIDAR_MAX = 5.0
PROXIMITY_MAX = 4.0

WARN_M = 0.60
STOP_M = 0.25

BATTERY_DRAIN_PER_SEC = 0.15  # percent while MOVING/ROTATING
LOW_BATTERY = 15.0

EVENT_BUFFER = 500
GOTO_ARRIVE_M = 0.05
HEADING_ARRIVE_RAD = 0.04

GRID_COLS = int(WORLD_WIDTH / TILE_SIZE)  # 15
GRID_ROWS = int(WORLD_HEIGHT / TILE_SIZE)  # 10
