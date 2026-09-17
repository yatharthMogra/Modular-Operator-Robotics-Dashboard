import type { EventMsg } from "../types";

function fmt(t: number): string {
  const d = new Date(t * 1000);
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  const ss = String(d.getSeconds()).padStart(2, "0");
  const ms = String(d.getMilliseconds()).padStart(3, "0");
  return `${hh}:${mm}:${ss}.${ms}`;
}

export function EventLog({ events }: { events: EventMsg[] }) {
  return (
    <section className="log">
      <div className="panel-label">EVENT LOG</div>
      <ul>
        {events.slice(0, 40).map((e, i) => (
          <li key={`${e.t}-${i}`} className={e.level}>
            <span className="ts">{fmt(e.t)}</span>
            {e.message}
          </li>
        ))}
        {events.length === 0 && <li className="muted">waiting for events</li>}
      </ul>
    </section>
  );
}
