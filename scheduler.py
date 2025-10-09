#!/usr/bin/env python3
# scheduler.py
# Process Scheduling Simulator: FCFS, SJF (non-preemptive), Round Robin (preemptive)
# Author: You
# License: MIT

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
import csv, argparse, math, sys

try:
    import matplotlib.pyplot as plt
    _HAS_MPL = True
except Exception:
    _HAS_MPL = False

@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    # Internal / derived fields (filled during simulation)
    remaining: int = field(init=False)
    first_start: Optional[int] = field(default=None)  # for Response Time
    completion: Optional[int] = field(default=None)

    def __post_init__(self):
        if self.burst <= 0:
            raise ValueError(f"Process {self.pid} has non-positive burst time.")
        if self.arrival < 0:
            raise ValueError(f"Process {self.pid} has negative arrival time.")
        self.remaining = self.burst
    def load_processes_from_csv(path: str) -> List[Process]:
    """
    CSV columns (header required): pid,arrival,burst
    Example:
      pid,arrival,burst
      P1,0,5
      P2,2,3
      P3,4,2
    """
    out: List[Process] = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            out.append(Process(
                pid=str(row['pid']).strip(),
                arrival=int(row['arrival']),
                burst=int(row['burst'])
            ))
    return out
    def deep_copy_procs(procs: List[Process]) -> List[Process]:
    # Create fresh (mutable) copies so one run doesn't affect another
    return [Process(p.pid, p.arrival, p.burst) for p in procs]
    def ascii_gantt(timeline: List[Tuple[int, int, Optional[str]]]) -> str:
    """
    timeline: list of (start, end, pid) where pid=None means CPU idle
    Returns a single multi-line string.
    """
    if not timeline:
        return "(empty timeline)"
        # Top bar and labels
    bar = []
    lbl = []
    ticks = []
    cursor = timeline[0][0]
    ticks.append(str(cursor))
    for (s, e, pid) in timeline:
        width = max(1, e - s)
        name = pid if pid is not None else "IDLE"
        seg = f"|{name:^{width*2}}"
        bar.append(seg)
        ticks.append(str(e))
    top = "".join(bar) + "|"
    # Build tick line aligned roughly under segment borders
    # (coarse approximation for CLI readability)
    tick_line = " ".join(ticks)
    return f"{top}\n{tick_line}"    
    
    def compute_metrics(procs: List[Process]) -> Dict[str, Dict[str, float]]:
    """
    Assumes completion & first_start set. Returns:
    {
      'per_process': {pid: {'WT':..., 'TAT':..., 'RT':..., 'CT':...}},
      'overall': {'AVG_WT':..., 'AVG_TAT':..., 'AVG_RT':..., 'THROUGHPUT':..., 'CPU_UTIL':...}
    }
    """
    n = len(procs)
    if n == 0:
        return {'per_process': {}, 'overall': {}}

    # Compute start/end of simulation
    min_arrival = min(p.arrival for p in procs)
    max_completion = max(p.completion or 0 for p in procs)

    total_busy = sum(p.burst for p in procs)
    total_time = max_completion - min_arrival if max_completion > min_arrival else 0
    cpu_util = (total_busy / total_time * 100.0) if total_time > 0 else 0.0
    throughput = n / total_time if total_time > 0 else float('inf') if n > 0 else 0.0

    per = {}
    sum_wt = sum_tat = sum_rt = 0.0
    for p in procs:
        if p.completion is None or p.first_start is None:
            raise RuntimeError(f"Process {p.pid} missing simulation fields.")
        tat = p.completion - p.arrival
        wt  = tat - p.burst
        rt  = p.first_start - p.arrival
        per[p.pid] = {'WT': wt, 'TAT': tat, 'RT': rt, 'CT': p.completion}
        sum_wt += wt
        sum_tat += tat
        sum_rt += rt

    overall = {
        'AVG_WT': sum_wt / n,
        'AVG_TAT': sum_tat / n,
        'AVG_RT': sum_rt / n,
        'THROUGHPUT': throughput,
        'CPU_UTIL': cpu_util
    }
    return {'per_process': per, 'overall': overall}
# ---- Scheduling Algorithms ----
    def simulate_fcfs(procs: List[Process]) -> List[Tuple[int, int, Optional[str]]]:
    """
    FCFS with arrival times. If CPU is idle and no process available, timeline records IDLE gap.
    Returns timeline list of (start, end, pid) segments.
    """
    P = deep_copy_procs(procs)
    # Sort by arrival, then by pid (stable tie-breaker)
    P.sort(key=lambda x: (x.arrival, x.pid))
    t = 0
    timeline: List[Tuple[int, int, Optional[str]]] = []
    for p in P:
        if t < p.arrival:
            # CPU idle
            timeline.append((t, p.arrival, None))
            t = p.arrival
        p.first_start = t
        start = t
        t += p.burst
        p.remaining = 0
        p.completion = t
        timeline.append((start, t, p.pid))
    # copy back computed fields to original matched by pid
    update_originals(procs, P)
    return coalesce_timeline(timeline)
    def simulate_sjf_nonpreemptive(procs: List[Process]) -> List[Tuple[int, int, Optional[str]]]:
    """
    SJF (non-preemptive) with arrival times.
    """
    P = deep_copy_procs(procs)
    t = min(p.arrival for p in P) if P else 0
    done = set()
    timeline: List[Tuple[int, int, Optional[str]]] = []
    while len(done) < len(P):
        ready = [p for p in P if p.arrival <= t and p.pid not in done]
        if not ready:
            # jump to next arrival
            next_t = min(p.arrival for p in P if p.pid not in done)
            if t < next_t:
                timeline.append((t, next_t, None))
                t = next_t
            continue
        # choose shortest burst among ready (tie: arrival, then pid)
        ready.sort(key=lambda x: (x.burst, x.arrival, x.pid))
        p = ready[0]
        p.first_start = t if p.first_start is None else p.first_start
        start = t
        t += p.burst
        p.remaining = 0
        p.completion = t
        done.add(p.pid)
        def simulate_rr(procs: List[Process], quantum: int) -> List[Tuple[int, int, Optional[str]]]:
    """
    Round Robin (preemptive) with arrival times and time quantum > 0.
    Uses a standard ready queue; on ties, lower arrival then pid order.
    """
    if quantum <= 0:
        raise ValueError("Quantum must be > 0 for Round Robin.")

    P = deep_copy_procs(procs)
    t = min((p.arrival for p in P), default=0)
    timeline: List[Tuple[int, int, Optional[str]]] = []

    # Ready queue holds indices into P
    ready: List[int] = []
    visited = set()  # to seed arrivals only once per time
    # helper to enqueue any arrived processes at time t
    def enqueue_arrivals(current_time: int):
        for i, p in enumerate(P):
            # add to ready when it has arrived and still has work and not in ready
            if p.arrival <= current_time and p.remaining > 0 and i not in ready:
                # avoid flooding: but order matters; we'll add in arrival order later
                pass
        # Build a deterministic ordering: by arrival then pid, include only those not already in ready and not finished
        newly = [i for i, p in enumerate(P) if p.arrival <= current_time and p.remaining > 0 and i not in ready]
        newly.sort(key=lambda i: (P[i].arrival, P[i].pid))
        for i in newly:
            ready.append(i)
        timeline.append((start, t, p.pid))
    update_originals(procs, P)
    return coalesce_timeline(timeline)
    def simulate_rr(procs: List[Process], quantum: int) -> List[Tuple[int, int, Optional[str]]]:
    """
    Round Robin (preemptive) with arrival times and time quantum > 0.
    Uses a standard ready queue; on ties, lower arrival then pid order.
    """
    if quantum <= 0:
        raise ValueError("Quantum must be > 0 for Round Robin.")

    P = deep_copy_procs(procs)
    t = min((p.arrival for p in P), default=0)
    timeline: List[Tuple[int, int, Optional[str]]] = []

    # Ready queue holds indices into P
    ready: List[int] = []
    visited = set()  # to seed arrivals only once per time
    # helper to enqueue any arrived processes at time t
    def enqueue_arrivals(current_time: int):
        for i, p in enumerate(P):
            # add to ready when it has arrived and still has work and not in ready
            if p.arrival <= current_time and p.remaining > 0 and i not in ready:
                # avoid flooding: but order matters; we'll add in arrival order later
                pass
        # Build a deterministic ordering: by arrival then pid, include only those not already in ready and not finished
        newly = [i for i, p in enumerate(P) if p.arrival <= current_time and p.remaining > 0 and i not in ready]
        newly.sort(key=lambda i: (P[i].arrival, P[i].pid))
        for i in newly:
            ready.append(i)

    # Initialize time to first arrival and push that/those into ready
    enqueue_arrivals(t)

    while any(p.remaining > 0 for p in P):
        if not ready:
            # CPU idle: jump to next arrival time
            future_arrivals = [p.arrival for p in P if p.remaining > 0 and p.arrival > t]
            if not future_arrivals:
                break  # nothing left somehow
            next_t = min(future_arrivals)
            if t < next_t:
                timeline.append((t, next_t, None))
                t = next_t
            enqueue_arrivals(t)
            if not ready:
                continue
         idx = ready.pop(0)
        p = P[idx]
        # Set response time if first run
        if p.first_start is None:
            p.first_start = t

        run = min(quantum, p.remaining)
        start = t
        t += run
        p.remaining -= run
        timeline.append((start, t, p.pid))
