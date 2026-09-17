# Modular Robotics Operator Console

A real-time operator console for a **simulated fleet of modular robotic tiles**.

You see the floor, inspect a tile, send a command, watch sensors, ask the fleet to form a conveyor, and you are told the truth when the server drops. Hardware is simulated so the loop can be finished: **operator → software → plant → operator**.

This is a research-style instrument, not a product dashboard.

## Walkthrough

A full pass through the operator console: live tiles, commands, sensors, safety stop, and conveyor configuration.

[![Operator console walkthrough](https://drive.google.com/thumbnail?id=13rMH3wDOZ5m6KcJBCuB6awIvuRzt1v8d&sz=w1280)](https://drive.google.com/file/d/13rMH3wDOZ5m6KcJBCuB6awIvuRzt1v8d/view?usp=sharing)

[Watch the walkthrough](https://drive.google.com/file/d/13rMH3wDOZ5m6KcJBCuB6awIvuRzt1v8d/view?usp=sharing)

## The problem

Modular robots are not one machine. They are many identical tiles that are supposed to *become* something useful — a line, a conveyor, a surface.

That only works if a person can:

- see where every tile is
- command one, or the whole formation
- trust proximity and LiDAR when something is in the way
- notice when the central system has gone quiet

Without that loop you have squares on a screen, not a system you can run.

## What it does

Eight tiles live in a 12 × 8 m arena.

- **Live map** — positions, headings, obstacles, selected-tile LiDAR rays
- **Inspector** — pose, speed, battery, four proximity beams
- **LiDAR** — 72-ray polar view for the selected tile
- **Commands** — body-relative move, rotate ±90°, stop, reset (with server acknowledgements)
- **Safety** — warning below ~0.6 m front range, emergency stop below ~0.25 m; move is refused until reset
- **Configuration** — pick start/end on the map, generate a conveyor; tiles drive to slots and align
- **Event log** — commands, acks, state changes, warnings
- **Connection** — `CONNECTED` / `RECONNECTING` / `OFFLINE`, sim Hz vs client Hz, last update; last snapshot freezes when the link dies

N on the pad is **forward along the tile heading** (the chevron), not “up on the map.”

## How it works

```text
Operator
   │
   ▼
React / TypeScript console
   │  REST (snapshot, health) + WebSocket (live path)
   ▼
FastAPI central server
   │  command router · state · events · connections
   ▼
In-process tile simulator
   │  motion · FSM · LiDAR · proximity · battery
   ▼
20 Hz snapshots back to the console
```

**REST** is for bootstrap and debug (`/api/snapshot`, `/api/health`, `/api/events`).
**WebSockets** carry commands, `command_ack` (accepted / rejected), telemetry, and events.

A command is not a local animation:

1. UI sends `{ type: "command", request_id, tile_id, action, payload }`
2. Server validates and acks
3. Simulator integrates motion and sensors at 20 Hz
4. Snapshots stream back; the map and inspector follow

The simulator runs **inside** FastAPI on purpose — two processes to run the whole prototype (`uvicorn` + Vite). Conveyor layout is a simple grid BFS plus greedy assignment. That is a demonstration of commanding a formation, not a planning paper.

Safety states live in the plant: `IDLE` → `MOVING` / `ROTATING` → `WARNING` → `STOP`. The UI reflects them; it does not invent them.

On reconnect the client loads a REST snapshot, then resumes the socket, so the browser does not guess the world.

## Stack

| Layer | Choice |
| --- | --- |
| Console | React, TypeScript, Vite, SVG |
| Server | Python, FastAPI, WebSockets |
| Plant | In-process simulator (NumPy for ray samples) |

No database, Docker, auth, ROS, or ML. Those are out of scope so the human–robot loop stays the point.

## Run

Python 3.9+ (3.11 preferred), Node 20+. Two terminals.

```bash
# backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# frontend
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies `/api` and `/ws` to port 8000.

```bash
cd backend && source .venv/bin/activate && pytest
```

Tests cover the motion FSM, the conveyor planner, and command → simulator → snapshot.

## Try it

1. Confirm the header is `CONNECTED`, SIM ~20 Hz, eight tiles live.
2. Click a tile, press **N** — event log should show `command_ack accepted`, then `MOVING`.
3. **CCW 90** so the chevron faces the top obstacle, then **N**. Watch LiDAR and front proximity. Expect **WARNING**, then emergency **STOP**.
4. **RESET**, then **GENERATE CONFIGURATION** with start `(2, 4)` and end `(9, 4)` (defaults). Tiles form a line.
5. Stop the backend. Header goes `RECONNECTING` → `OFFLINE`; last update freezes. Start uvicorn again; live ticks resume.

A timed walkthrough: [docs/demo-script.md](docs/demo-script.md).
Why the UI looks like a lab console: [docs/design.md](docs/design.md), [docs/wireframe.svg](docs/wireframe.svg).

World frame: origin top-left, +x right, +y down (SVG-aligned). Heading 0 faces +x.

## Layout

```text
backend/app/          FastAPI, protocol, simulator, FSM, planner
backend/tests/        FSM, planner, command-flow
frontend/src/         console, map, inspector, LiDAR, socket hook
docs/                 design notes, wireframe, demo script
```
