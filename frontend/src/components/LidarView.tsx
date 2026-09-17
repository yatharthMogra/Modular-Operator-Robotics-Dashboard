import type { Tile } from "../types";

const LIDAR_MAX = 5;

export function LidarView({ tile }: { tile: Tile | null }) {
  const cx = 90;
  const cy = 90;
  const R = 72;
  return (
    <section className="panel">
      <div className="panel-label">LIDAR</div>
      <svg className="lidar" viewBox="0 0 180 180">
        <circle cx={cx} cy={cy} r={R} className="ring" />
        <circle cx={cx} cy={cy} r={R * 0.5} className="ring" />
        {tile?.lidar.map((hit, i) => {
          const frac = Math.min(hit.range / LIDAR_MAX, 1);
          const len = frac * R;
          const x2 = cx + len * Math.sin(hit.angle);
          const y2 = cy - len * Math.cos(hit.angle);
          return <line key={i} className="lidar-ray" x1={cx} y1={cy} x2={x2} y2={y2} />;
        })}
        <polygon points={`${cx},${cy - 10} ${cx + 6},${cy + 6} ${cx - 6},${cy + 6}`} className="chevron" />
      </svg>
    </section>
  );
}
