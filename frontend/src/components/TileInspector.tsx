import type { Tile } from "../types";

function speed(t: Tile): number {
  return Math.hypot(t.vx, t.vy);
}

export function TileInspector({ tile }: { tile: Tile | null }) {
  if (!tile) {
    return (
      <section className="panel">
        <div className="panel-label">INSPECTOR</div>
        <div className="muted">SELECT A TILE</div>
      </section>
    );
  }
  const deg = ((tile.theta * 180) / Math.PI + 360) % 360;
  const p = tile.proximity;
  return (
    <section className="panel">
      <div className="panel-label">TILE {tile.id}</div>
      <div className={`state ${tile.state.toLowerCase()}`}>{tile.state}</div>
      <dl className="kv">
        <dt>POS</dt>
        <dd>
          {tile.x.toFixed(2)}, {tile.y.toFixed(2)}
        </dd>
        <dt>HEADING</dt>
        <dd>{deg.toFixed(1)} deg</dd>
        <dt>SPEED</dt>
        <dd>{speed(tile).toFixed(2)} m/s</dd>
        <dt>BATTERY</dt>
        <dd>{tile.battery.toFixed(0)}%</dd>
      </dl>
      <div className="panel-label tight">PROXIMITY</div>
      <div className="prox">
        F {p.front.toFixed(2)}m&nbsp; L {p.left.toFixed(2)}m&nbsp; R {p.right.toFixed(2)}m&nbsp; B {p.rear.toFixed(2)}m
      </div>
    </section>
  );
}
