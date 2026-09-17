from app.config import STOP_M, WARN_M
from app.simulator.fsm import step_fsm
from app.simulator.tile import Tile


def test_idle_move_becomes_moving():
    state, emergency, msg = step_fsm(
        state="IDLE",
        front=2.0,
        has_move=True,
        has_rotate=False,
        motion_done=False,
        emergency=False,
    )
    assert state == "MOVING"
    assert emergency is False
    assert msg == "MOVING"


def test_moving_warns_under_threshold():
    state, emergency, msg = step_fsm(
        state="MOVING",
        front=WARN_M - 0.05,
        has_move=True,
        has_rotate=False,
        motion_done=False,
        emergency=False,
    )
    assert state == "WARNING"
    assert emergency is False
    assert "warning" in (msg or "")


def test_warning_emergency_stop():
    state, emergency, msg = step_fsm(
        state="WARNING",
        front=STOP_M - 0.05,
        has_move=True,
        has_rotate=False,
        motion_done=False,
        emergency=False,
    )
    assert state == "STOP"
    assert emergency is True
    assert msg == "emergency stop"


def test_emergency_refuses_move_until_reset():
    tile = Tile("07", 5.0, 4.0, 0.0)
    tile.apply_stop(emergency=True)
    assert tile.apply_move(0.0, 1.0) == "unsafe_state"
    tile.reset()
    assert tile.state == "IDLE"
    assert tile.apply_move(0.0, 1.0) is None
    assert tile.state == "MOVING"
