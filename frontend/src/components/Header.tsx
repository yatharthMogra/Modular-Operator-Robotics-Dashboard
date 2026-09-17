import type { ConnStatus } from "../types";

function fmtTime(t: number | null): string {
  if (t == null) return "—";
  const d = new Date(t * 1000);
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  const ss = String(d.getSeconds()).padStart(2, "0");
  const ms = String(d.getMilliseconds()).padStart(3, "0");
  return `${hh}:${mm}:${ss}.${ms}`;
}

export function Header(props: {
  status: ConnStatus;
  simHz: number;
  clientHz: number;
  lastUpdate: number | null;
}) {
  const cls =
    props.status === "CONNECTED" ? "ok" : props.status === "RECONNECTING" ? "warn" : "err";
  return (
    <header className="hdr">
      <div>
        <div className="title">MODULAR ROBOTICS OPERATOR CONSOLE</div>
        <div className="sub">REAL-TIME HUMAN-ROBOT INTERACTION AND SYSTEMS INTEGRATION PROTOTYPE</div>
      </div>
      <div className="hdr-meta">
        <span className={`pill ${cls}`}>
          <span className="dot" />
          SERVER {props.status}
        </span>
        <span>SIM {props.simHz.toFixed(1)} Hz</span>
        <span>CLIENT {props.clientHz.toFixed(1)} Hz</span>
        <span>LAST {fmtTime(props.lastUpdate)}</span>
      </div>
    </header>
  );
}
