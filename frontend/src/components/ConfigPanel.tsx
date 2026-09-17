export function ConfigPanel(props: {
  configMode: boolean;
  start: [number, number] | null;
  end: [number, number] | null;
  disabled: boolean;
  onToggle: () => void;
  onGenerate: () => void;
  onClear: () => void;
}) {
  const start = props.start ? `(${props.start[0]}, ${props.start[1]})` : "—";
  const end = props.end ? `(${props.end[0]}, ${props.end[1]})` : "—";
  return (
    <section className="panel">
      <div className="panel-label">CONFIGURATION</div>
      <p className="hint">Pick START then END on the map, then generate a conveyor line.</p>
      <div className="kv-inline">
        START {start}
        <br />
        END {end}
      </div>
      <div className="pad-row">
        <button type="button" className={props.configMode ? "on" : ""} onClick={props.onToggle}>
          {props.configMode ? "PICKING" : "PICK CELLS"}
        </button>
        <button type="button" onClick={props.onClear}>
          CLEAR
        </button>
      </div>
      <button
        type="button"
        className="wide"
        disabled={props.disabled || !props.start || !props.end}
        onClick={props.onGenerate}
      >
        GENERATE CONFIGURATION
      </button>
    </section>
  );
}
