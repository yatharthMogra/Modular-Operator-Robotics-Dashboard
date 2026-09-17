import { useMemo, useState } from "react";
import { CommandPad } from "./components/CommandPad";
import { ConfigPanel } from "./components/ConfigPanel";
import { EventLog } from "./components/EventLog";
import { Header } from "./components/Header";
import { LidarView } from "./components/LidarView";
import { RobotMap } from "./components/RobotMap";
import { TileInspector } from "./components/TileInspector";
import { useRobotSocket } from "./ws/useRobotSocket";

export default function App() {
  const sock = useRobotSocket();
  const [selectedId, setSelectedId] = useState<string | null>("03");
  const [configMode, setConfigMode] = useState(false);
  const [start, setStart] = useState<[number, number] | null>([2, 4]);
  const [end, setEnd] = useState<[number, number] | null>([9, 4]);

  const tile = useMemo(
    () => sock.tiles.find((t) => t.id === selectedId) ?? sock.tiles[0] ?? null,
    [sock.tiles, selectedId],
  );
  const connected = sock.status === "CONNECTED";

  const pickCell = (col: number, row: number) => {
    if (!start || (start && end)) {
      setStart([col, row]);
      setEnd(null);
      return;
    }
    setEnd([col, row]);
  };

  return (
    <div className="console">
      <Header status={sock.status} simHz={sock.simHz} clientHz={sock.clientHz} lastUpdate={sock.lastUpdate} />
      <div className="main">
        <RobotMap
          world={sock.world}
          tiles={sock.tiles}
          selectedId={tile?.id ?? null}
          onSelect={(id) => {
            setConfigMode(false);
            setSelectedId(id);
          }}
          configMode={configMode}
          start={start}
          end={end}
          onPickCell={pickCell}
        />
        <aside className="side">
          <TileInspector tile={tile} />
          <LidarView tile={tile} />
          <CommandPad
            disabled={!connected || !tile}
            onMove={(fx, fy) => tile && sock.sendCommand(tile.id, "MOVE", { fx, fy })}
            onRotate={(d) => tile && sock.sendCommand(tile.id, "ROTATE", { delta_deg: d })}
            onStop={() => tile && sock.sendCommand(tile.id, "STOP")}
            onReset={() => tile && sock.sendCommand(tile.id, "RESET")}
          />
          <ConfigPanel
            configMode={configMode}
            start={start}
            end={end}
            disabled={!connected}
            onToggle={() => setConfigMode((v) => !v)}
            onClear={() => {
              setStart(null);
              setEnd(null);
            }}
            onGenerate={() => {
              if (start && end) sock.sendConfigure(start, end);
            }}
          />
        </aside>
      </div>
      <EventLog events={sock.events} />
    </div>
  );
}
