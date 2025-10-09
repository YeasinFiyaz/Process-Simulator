# procsim/sim/utils.py
from typing import List, Optional, Tuple

Seg = Tuple[int, int, Optional[str]]  # start, end, pid or None (idle)

def ascii_gantt(timeline: List[Seg]) -> str:
    if not timeline:
        return "(empty timeline)"
    bar, ticks = [], [str(timeline[0][0])]
    for (s, e, pid) in timeline:
        width = max(1, e - s)
        name = pid if pid is not None else "IDLE"
        seg = f"|{name:^{width*2}}"
        bar.append(seg)
        ticks.append(str(e))
    top = "".join(bar) + "|"
    return f"{top}\n{' '.join(ticks)}"

def svg_gantt(timeline: List[Seg]) -> str:
    """Return a compact SVG string for the timeline."""
    if not timeline:
        return "<svg width='600' height='120'></svg>"

    pids = sorted({pid for _,_,pid in timeline if pid is not None})
    def row_for(pid): return (pids.index(pid) if pid else len(pids))
    rows = len(pids) + 1  # idle at bottom
    px = 40
    span = max(e for _,e,_ in timeline)
    height = 40 * rows + 50
    width = max(600, (span + 2) * px)

    # Bars
    rects = []
    labels = []
    for (s, e, pid) in timeline:
        y = 45 + row_for(pid) * 40
        x = (s + 1) * px
        w = (e - s) * px
        fill = "#999999" if pid is None else _color_for_pid(pid, pids)
        rects.append(f"<rect x='{x}' y='{y}' width='{w}' height='24' rx='6' ry='6' fill='{fill}' opacity='{0.35 if pid is None else 0.85}'/>")
        label = "IDLE" if pid is None else pid
        labels.append(f"<text x='{x + w/2}' y='{y + 16}' font-size='12' fill='#fff' text-anchor='middle'>{label}</text>")

    # Grid + ticks
    grid = []
    for i in range(span + 1):
        x = (i + 1) * px
        grid.append(f"<line x1='{x}' y1='20' x2='{x}' y2='{height-20}' stroke='#eee'/>")
        grid.append(f"<text x='{x-4}' y='{height-6}' font-size='11' fill='#666'>{i}</text>")

    ylabels = [f"<text x='10' y='{60 + i*40}' font-size='12' fill='#555'>{pid}</text>" for i,pid in enumerate(pids)]
    ylabels.append(f"<text x='10' y='{60 + len(pids)*40}' font-size='12' fill='#555'>IDLE</text>")

    svg = f"""
<svg width='{width}' height='{height}' class='rounded-xl border bg-white' xmlns='http://www.w3.org/2000/svg'>
  <g>{''.join(grid)}</g>
  <g>{''.join(ylabels)}</g>
  <g>{''.join(rects)}</g>
  <g>{''.join(labels)}</g>
  <text x='10' y='16' font-size='12' fill='#333'>Time →</text>
</svg>
"""
    return svg

def _color_for_pid(pid: str, pids: list) -> str:
    # simple HSL wheel
    i = pids.index(pid)
    hue = (i * 67) % 360
    return f"hsl({hue},80%,45%)"
