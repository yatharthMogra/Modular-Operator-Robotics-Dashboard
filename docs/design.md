# Operator console — design decisions

The interface is a **research / lab operator console**, not a product dashboard. Spatial state is the job; chrome stays out of the way.

1. **The map occupies the largest area** because spatial state is the operator’s primary information. Tiles, headings, obstacles, and LiDAR hits are understood in the world, not in a table.
2. **Telemetry lives in a fixed inspector**, not as overlays on the map. Pose, battery, and proximity change every tick; overlaying them would clutter the formation view.
3. **Warnings appear twice:** tile color on the map (where to look) and a line in the event log (what happened, when). Spatial + temporal, not one or the other.
4. **Commands are disabled** when no tile is selected or the server is not `CONNECTED`. A dead pad that still looks clickable would lie about closed-loop control.
5. **Connection state is always in the header.** `CONNECTED` / `RECONNECTING` / `OFFLINE` plus last-update time is the systems-health story; it must not be buried in a settings panel.
6. **Sim Hz, client Hz, and last update are shown separately.** The plant ticks at 20 Hz; the network delivers snapshots; the UI renders them. Those are three layers. Displaying them makes the live pipeline observable without premature render throttling.
7. **Configuration is a mode, not a second app.** Start/end are picked on the same map the operator already uses to drive tiles. Generate is one command into the same WebSocket.
8. **Monospace, 1px rules, muted industrial color.** No gradients, cards, or welcome copy. The UI should read as an instrument, not a SaaS shell.
9. **Selected-tile LiDAR is both polar (inspector) and faint rays on the map.** Polar is for range structure; map overlay is for “what is that hit in the world?”
10. **The event log is a ring, newest first, always visible.** Debugging a STOP is an operator task. If the log were a modal, the safety story would disappear at the moment it matters.
