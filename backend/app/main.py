from __future__ import annotations

import asyncio
import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import TICK_HZ
from app.managers.connections import ConnectionManager
from app.managers.events import EventLog
from app.models import CommandIn, ConfigureIn
from app.router import handle_command, handle_configure
from app.simulator.engine import Simulator


async def run_ticker(app: FastAPI) -> None:
    dt = 1.0 / TICK_HZ
    while True:
        sim: Simulator = app.state.sim
        events: EventLog = app.state.events
        connections: ConnectionManager = app.state.connections
        for raw in sim.step(dt):
            ev = events.emit(
                raw["message"],
                level=raw.get("level", "info"),
                tile_id=raw.get("tile_id"),
            )
            await connections.broadcast(ev)
        await connections.broadcast(sim.snapshot_message())
        await asyncio.sleep(dt)


def create_app(*, enable_ticker: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.sim = Simulator()
        app.state.events = EventLog()
        app.state.connections = ConnectionManager()
        task = None
        if enable_ticker:
            task = asyncio.create_task(run_ticker(app))
        yield
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    app = FastAPI(title="Modular Robotics Operator Console", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health():
        return {
            "status": "ok",
            "tick_hz": TICK_HZ,
            "clients": app.state.connections.count,
        }

    @app.get("/api/snapshot")
    def snapshot():
        return app.state.sim.snapshot_message()

    @app.get("/api/events")
    def events(limit: int = Query(100, ge=1, le=500)):
        return {"events": app.state.events.list(limit)}

    @app.post("/api/command")
    def command(body: CommandIn):
        ack, _ = handle_command(
            app.state.sim,
            app.state.events,
            body.request_id,
            body.tile_id,
            body.action,
            body.payload,
        )
        return ack

    @app.post("/api/configure")
    def configure(body: ConfigureIn):
        ack, _ = handle_configure(
            app.state.sim,
            app.state.events,
            body.request_id,
            tuple(body.start),
            tuple(body.end),
        )
        return ack

    @app.websocket("/ws")
    async def ws_endpoint(ws: WebSocket):
        connections: ConnectionManager = app.state.connections
        sim: Simulator = app.state.sim
        events: EventLog = app.state.events
        await connections.connect(ws)
        await connections.send(ws, sim.snapshot_message())
        try:
            while True:
                data = await ws.receive_json()
                msg_type = data.get("type")
                if msg_type == "command":
                    ack, evs = handle_command(
                        sim,
                        events,
                        str(data.get("request_id", "")),
                        str(data.get("tile_id", "")),
                        str(data.get("action", "")),
                        data.get("payload") or {},
                    )
                    await connections.send(ws, ack)
                    for ev in evs:
                        await connections.broadcast(ev)
                elif msg_type == "configure":
                    start = data.get("start") or [2, 4]
                    end = data.get("end") or [9, 4]
                    ack, evs = handle_configure(
                        sim,
                        events,
                        str(data.get("request_id", "")),
                        (int(start[0]), int(start[1])),
                        (int(end[0]), int(end[1])),
                    )
                    await connections.send(ws, ack)
                    for ev in evs:
                        await connections.broadcast(ev)
        except WebSocketDisconnect:
            connections.disconnect(ws)
        except Exception:
            connections.disconnect(ws)

    return app


app = create_app()
