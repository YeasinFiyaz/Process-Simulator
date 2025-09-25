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
