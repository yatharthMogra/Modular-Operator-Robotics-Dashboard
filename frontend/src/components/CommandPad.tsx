const DIRS: { label: string; fx: number; fy: number }[] = [
  { label: "NW", fx: -1, fy: 1 },
  { label: "N", fx: 0, fy: 1 },
  { label: "NE", fx: 1, fy: 1 },
  { label: "W", fx: -1, fy: 0 },
  { label: "·", fx: 0, fy: 0 },
  { label: "E", fx: 1, fy: 0 },
  { label: "SW", fx: -1, fy: -1 },
  { label: "S", fx: 0, fy: -1 },
  { label: "SE", fx: 1, fy: -1 },
];

export function CommandPad(props: {
  disabled: boolean;
  onMove: (fx: number, fy: number) => void;
  onRotate: (delta: number) => void;
  onStop: () => void;
  onReset: () => void;
}) {
  return (
    <section className="panel">
      <div className="panel-label">COMMANDS</div>
      <div className="pad">
        {DIRS.map((d) => (
          <button
            key={d.label}
            type="button"
            disabled={props.disabled || (d.fx === 0 && d.fy === 0)}
            onClick={() => props.onMove(d.fx, d.fy)}
          >
            {d.label}
          </button>
        ))}
      </div>
      <div className="pad-row">
        <button type="button" disabled={props.disabled} onClick={() => props.onRotate(-90)}>
          CCW 90
        </button>
        <button type="button" disabled={props.disabled} onClick={() => props.onRotate(90)}>
          CW 90
        </button>
      </div>
      <div className="pad-row">
        <button type="button" className="danger" disabled={props.disabled} onClick={props.onStop}>
          STOP
        </button>
        <button type="button" disabled={props.disabled} onClick={props.onReset}>
          RESET
        </button>
      </div>
      <p className="hint">MOVE is body-relative. N is forward along heading.</p>
    </section>
  );
}
