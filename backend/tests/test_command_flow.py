from fastapi.testclient import TestClient

from app.main import create_app


def test_command_flow_move_updates_snapshot():
    app = create_app(enable_ticker=False)
    with TestClient(app) as client:
        body = {
            "type": "command",
            "request_id": "cmd-test-1",
            "tile_id": "01",
            "action": "MOVE",
            "payload": {"fx": 0, "fy": 1},
        }
        ack = client.post("/api/command", json=body).json()
        assert ack["status"] == "accepted"
        assert ack["request_id"] == "cmd-test-1"
        assert ack["state"] == "MOVING"

        sim = app.state.sim
        before = sim.tiles["01"].x
        for _ in range(5):
            sim.step(0.05)

        snap = client.get("/api/snapshot").json()
        tile = next(t for t in snap["tiles"] if t["id"] == "01")
        assert tile["state"] == "MOVING"
        assert tile["x"] > before
        speed = (tile["vx"] ** 2 + tile["vy"] ** 2) ** 0.5
        assert speed > 0.1
