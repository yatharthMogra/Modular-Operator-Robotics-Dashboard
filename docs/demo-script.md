# Demo script (2–3 minutes)

Narrate closed-loop control, not the planner. Screen: operator console at `http://localhost:5173`.

| Time | Beat | What to show |
|------|------|----------------|
| 0:00 | Start | Both processes up. Header `CONNECTED`, SIM ~20 Hz, CLIENT ~20 Hz, eight scattered tiles live. |
| 0:15 | Select | Click tile `03`. Inspector: pose, heading, battery, proximity. Polar LiDAR inset. |
| 0:25 | Command | MOVE forward. Event log: `command_ack accepted`, then `MOVING`. Tile translates; telemetry ticks. |
| 0:45 | Sensors | CCW 90 so the chevron points at the top obstacle, then N (forward). LiDAR rays shorten; front proximity drops. |
| 1:00 | WARNING | Front < 0.60 m: tile amber, log warning. Still streaming. |
| 1:10 | STOP | Front < 0.25 m: emergency STOP, red, motion dead. Mention FSM + refused MOVE until RESET. |
| 1:25 | RESET | RESET → spawn, IDLE. Optional: MOVE accepted again. |
| 1:35 | Configure | Config mode. Start `(2,4)`, end `(9,4)`. Generate. Tiles drive to a line and align. Log: formation complete. *This is operator intent → plant, not a planning paper.* |
| 2:10 | Drop | Kill uvicorn. Header `RECONNECTING` then `OFFLINE`. Last snapshot frozen; last-update timestamp stuck. CLIENT Hz → 0. |
| 2:25 | Recover | Restart uvicorn. Snapshot bootstrap, `CONNECTED`, live ticks resume. |
| 2:40 | Close | One sentence: bidirectional WebSocket, acks, 20 Hz telemetry, safety FSM, connection recovery on a modular tile plant. |

If something fails, do not improvise extra features. Restart both processes and pick up at the next beat.
