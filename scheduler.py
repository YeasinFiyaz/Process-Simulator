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
