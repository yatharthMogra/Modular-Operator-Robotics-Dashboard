import { useCallback, useEffect, useRef, useState } from "react";
import type { ConnStatus, EventMsg, Snapshot, Tile, World } from "../types";

const BACKOFF_MS = [500, 1000, 2000, 5000];

function requestId(prefix: string): string {
  return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`;
}

export function useRobotSocket() {
  const [status, setStatus] = useState<ConnStatus>("RECONNECTING");
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [events, setEvents] = useState<EventMsg[]>([]);
  const [lastUpdate, setLastUpdate] = useState<number | null>(null);
  const [simHz, setSimHz] = useState(20);
  const [clientHz, setClientHz] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const failCount = useRef(0);
  const timerRef = useRef<number | null>(null);
  const stampsRef = useRef<number[]>([]);
  const stopped = useRef(false);

  const pushEvent = useCallback((ev: EventMsg) => {
    setEvents((prev) => [ev, ...prev].slice(0, 200));
  }, []);

  const applySnapshot = useCallback((snap: Snapshot) => {
    setSnapshot(snap);
    setSimHz(snap.tick_hz);
    setLastUpdate(snap.t);
    const now = Date.now();
    const stamps = stampsRef.current.filter((t) => now - t < 1000);
    stamps.push(now);
    stampsRef.current = stamps;
    setClientHz(stamps.length);
  }, []);

  useEffect(() => {
    stopped.current = false;

    const connect = () => {
      if (stopped.current) return;
      const proto = window.location.protocol === "https:" ? "wss" : "ws";
      const url = `${proto}://${window.location.host}/ws`;
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        failCount.current = 0;
        setStatus("CONNECTED");
        fetch("/api/snapshot")
          .then((r) => r.json())
          .then((snap: Snapshot) => applySnapshot(snap))
          .catch(() => undefined);
      };

      ws.onmessage = (ev) => {
        let msg: unknown;
        try {
          msg = JSON.parse(ev.data);
        } catch {
          return;
        }
        const typed = msg as { type?: string };
        if (typed.type === "snapshot") {
          applySnapshot(msg as Snapshot);
        } else if (typed.type === "event") {
          pushEvent(msg as EventMsg);
        } else if (typed.type === "command_ack") {
          const ack = msg as {
            request_id: string;
            status: string;
            reason: string | null;
            state: string | null;
          };
          pushEvent({
            type: "event",
            t: Date.now() / 1000,
            level: ack.status === "accepted" ? "info" : "warn",
            tile_id: null,
            message: `${ack.request_id} ${ack.status}${ack.reason ? ` (${ack.reason})` : ""}${ack.state ? ` → ${ack.state}` : ""}`,
            request_id: ack.request_id,
          });
        }
      };

      ws.onclose = () => {
        if (stopped.current || wsRef.current !== ws) return;
        wsRef.current = null;
        failCount.current += 1;
        setStatus(failCount.current >= 3 ? "OFFLINE" : "RECONNECTING");
        setClientHz(0);
        const delay = BACKOFF_MS[Math.min(failCount.current - 1, BACKOFF_MS.length - 1)];
        timerRef.current = window.setTimeout(connect, delay);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    connect();
    return () => {
      stopped.current = true;
      if (timerRef.current != null) window.clearTimeout(timerRef.current);
      wsRef.current?.close();
    };
  }, [applySnapshot, pushEvent]);

  const send = useCallback((payload: unknown) => {
    const ws = wsRef.current;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      pushEvent({
        type: "event",
        t: Date.now() / 1000,
        level: "warn",
        tile_id: null,
        message: "command dropped: not CONNECTED",
      });
      return;
    }
    ws.send(JSON.stringify(payload));
  }, [pushEvent]);

  const sendCommand = useCallback(
    (tileId: string, action: string, payload: Record<string, number> = {}) => {
      send({
        type: "command",
        request_id: requestId("cmd"),
        tile_id: tileId,
        action,
        payload,
      });
    },
    [send],
  );

  const sendConfigure = useCallback(
    (start: [number, number], end: [number, number]) => {
      send({
        type: "configure",
        request_id: requestId("cfg"),
        start,
        end,
      });
    },
    [send],
  );

  const tiles: Tile[] = snapshot?.tiles ?? [];
  const world: World | null = snapshot?.world ?? null;

  return {
    status,
    tiles,
    world,
    events,
    lastUpdate,
    simHz,
    clientHz,
    sendCommand,
    sendConfigure,
  };
}
