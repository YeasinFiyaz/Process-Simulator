# Process Simulator (CLI) — FCFS / SJF / Round-Robin

A Python command-line app that simulates classic CPU scheduling algorithms and prints neat ASCII Gantt charts, per-process metrics, and summary stats.

#  Features

Algorithms: FCFS, non-preemptive SJF, and Round-Robin (preemptive).

Inputs: Inline via CLI, JSON file, or CSV.

Outputs:

ASCII Gantt chart

Per-process Waiting, Turnaround, Response times

CPU Utilization, Throughput, Context Switches, Avg metrics

Edge cases handled: idle CPU gaps, ties, zero arrival times, variable quanta, non-zero arrivals.

Deterministic tie-breaking (PID) for reproducible results.

Library mode (import functions in your own scripts).

Color output toggle (optional).


# Algorithms

FCFS (First-Come, First-Served): Non-preemptive, ordered by arrival, FIFO.

SJF (Shortest Job First): Non-preemptive, picks shortest remaining job among arrived; ties by arrival then PID.

Round-Robin (RR): Preemptive, fixed time quantum, fair time slicing among ready processes

# Roadmap

 - Preemptive SJF (SRTF)

 - Priority (pre/non-preemptive)

 - I/O bursts & Gantt for I/O

 - HTML/PNG chart export

 - Interactive TUI mode

 - Probabilistic workload generator

# CLI Usage: 
Usage: proc-sim [ALGO] [OPTIONS]

ALGO:
  fcfs                First-Come, First-Served
  sjf                 Shortest Job First (non-preemptive)
  rr                  Round-Robin (preemptive)

Input (choose one):
  --procs  "PID,AT,BT" ...   Inline processes (repeatable)
  --json   PATH              JSON array with pid/arrival/burst
  --csv    PATH              CSV with columns: pid,arrival,burst

Options:
  --quantum INT              Time quantum for RR (required for rr)
  --context-overhead INT     Context switch cost (default: 0)
  --color / --no-color       Colored output (default: color)
  --sort-pid                 Stable tie-break on PID (default on)
  --export PATH              Save results as JSON
  -q, --quiet                Only print metrics (no chart)
  -h, --help


# Acknowledgements

Built for students learning OS scheduling and for anyone who likes pretty ASCII timelines. Inspired by classic OS textbooks and lab exercises.
