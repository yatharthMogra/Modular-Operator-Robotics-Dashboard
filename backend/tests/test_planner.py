from app.simulator.planner import bfs_path, cell_center, plan_conveyor
from app.simulator.tile import spawn_tiles


def test_horizontal_conveyor_path():
    path = bfs_path((2, 4), (9, 4))
    assert path is not None
    assert path[0] == (2, 4)
    assert path[-1] == (9, 4)
    assert len(path) == 8
    for i, (c, r) in enumerate(path):
        assert r == 4
        assert c == 2 + i


def test_assignment_matches_path_length():
    tiles = list(spawn_tiles().values())
    planned = plan_conveyor((2, 4), (9, 4), tiles)
    assert planned is not None
    assert len(planned) == 8
    slots = {id(tile): slot for tile, slot in planned}
    assert len(slots) == 8
    xs = sorted(slot[0] for slot in slots.values())
    first = cell_center(2, 4)[0]
    last = cell_center(9, 4)[0]
    assert xs[0] == first
    assert xs[-1] == last
