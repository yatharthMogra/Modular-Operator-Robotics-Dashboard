from __future__ import annotations

import asyncio

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._clients: dict[WebSocket, asyncio.Lock] = {}

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._clients[ws] = asyncio.Lock()

    def disconnect(self, ws: WebSocket) -> None:
        self._clients.pop(ws, None)

    @property
    def count(self) -> int:
        return len(self._clients)

    async def send(self, ws: WebSocket, message: dict) -> None:
        lock = self._clients.get(ws)
        if lock is None:
            return
        async with lock:
            await ws.send_json(message)

    async def broadcast(self, message: dict) -> None:
        dead: list[WebSocket] = []
        for ws, lock in list(self._clients.items()):
            try:
                async with lock:
                    await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._clients.pop(ws, None)
