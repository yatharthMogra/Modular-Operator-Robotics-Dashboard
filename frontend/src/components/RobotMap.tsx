import type { MouseEvent, ReactNode } from "react";
import type { Tile, World } from "../types";

const STATE_STROKE: Record<string, string> = {
  IDLE: "#8a8a82",
  MOVING: "#3d7a4a",
  ROTATING: "#3d7a4a",
  WARNING: "#c4a035",
  STOP: "#b54a3a",
  OFFLINE: "#3a3a3a",
};

export function RobotMap(props: {
  world: World | null;
  tiles: Tile[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  configMode: boolean;
  start: [number, number] | null;
  end: [number, number] | null;
  onPickCell: (col: number, row: number) => void;
}) {
  const world = props.world;
  if (!world) {
    return <div className="map empty">NO SNAPSHOT</div>;
  }
  const { width, height, tile_size: ts, obstacles } = world;
  const selected = props.tiles.find((t) => t.id === props.selectedId);

  const onClick = (e: MouseEvent<SVGSVGElement>) => {
    const svg = e.currentTarget;
    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const ctm = svg.getScreenCTM();
    if (!ctm) return;
    const loc = pt.matrixTransform(ctm.inverse());
    if (props.configMode) {
      const col = Math.floor(loc.x / ts);
      const row = Math.floor(loc.y / ts);
      props.onPickCell(col, row);
      return;
    }
    const hit = props.tiles.find((t) => Math.abs(t.x - loc.x) <= ts / 2 && Math.abs(t.y - loc.y) <= ts / 2);
    if (hit) props.onSelect(hit.id);
  };

  const grid: ReactNode[] = [];
  for (let x = 0; x <= width; x += 1) {
    grid.push(<line key={`vx${x}`} x1={x} y1={0} x2={x} y2={height} />);
  }
  for (let y = 0; y <= height; y += 1) {
    grid.push(<line key={`hy${y}`} x1={0} y1={y} x2={width} y2={y} />);
  }

  const cellRect = (cell: [number, number], cls: string) => (
    <rect
      key={cls + cell.join(",")}
      className={cls}
      x={cell[0] * ts}
      y={cell[1] * ts}
      width={ts}
      height={ts}
    />
  );

  return (
    <svg className="map" viewBox={`0 0 ${width} ${height}`} onClick={onClick} role="img" aria-label="Robot map">
      <rect className="map-bg" x={0} y={0} width={width} height={height} />
      <g className="grid">{grid}</g>
      {props.start && cellRect(props.start, "cell-start")}
      {props.end && cellRect(props.end, "cell-end")}
      {obstacles.map((o, i) => (
        <rect key={i} className="obstacle" x={o.x} y={o.y} width={o.w} height={o.h} />
      ))}
      {selected &&
        selected.lidar.map((hit, i) => {
          const a = selected.theta + hit.angle;
          const x2 = selected.x + hit.range * Math.cos(a);
          const y2 = selected.y + hit.range * Math.sin(a);
          return <line key={i} className="lidar-ray" x1={selected.x} y1={selected.y} x2={x2} y2={y2} />;
        })}
      {props.tiles.map((t) => {
        const stroke = STATE_STROKE[t.state] ?? "#8a8a82";
        const half = ts / 2;
        const chevron = `M ${half * 0.15} 0 L ${-half * 0.22} ${-half * 0.28} L ${-half * 0.22} ${half * 0.28} Z`;
        return (
          <g key={t.id} transform={`translate(${t.x} ${t.y}) rotate(${(t.theta * 180) / Math.PI})`}>
            <rect
              className={t.id === props.selectedId ? "tile selected" : "tile"}
              x={-half}
              y={-half}
              width={ts}
              height={ts}
              stroke={stroke}
            />
            <path d={chevron} className="chevron" />
            <text className="tile-id" x={0} y={0.12} transform={`rotate(${(-t.theta * 180) / Math.PI})`}>
              {t.id}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
