# procsim/sim/views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from .forms import SimForm
from .utils import ascii_gantt, svg_gantt
from .scheduler import (
    Process, deep_copy_procs,
    simulate_fcfs, simulate_sjf_nonpreemptive, simulate_rr,
    compute_metrics
)

def index(request: HttpRequest):
    context = {"form": SimForm(initial={"algorithm":"fcfs","quantum":2})}
    if request.method == "POST":
        form = SimForm(request.POST, request.FILES)
        if form.is_valid():
            algo = form.cleaned_data["algorithm"]
            quantum = form.cleaned_data.get("quantum") or 2
            procs_in = form.cleaned_data["procs"]

            # Build Process objects and a fresh copy for each run
            procs = [Process(p["pid"], p["arrival"], p["burst"]) for p in procs_in]
            base = deep_copy_procs(procs)

            if algo == "fcfs":
                timeline = simulate_fcfs(base)
                algoname = "FCFS"
            elif algo == "sjf":
                timeline = simulate_sjf_nonpreemptive(base)
                algoname = "SJF (Non-Preemptive)"
            else:
                timeline = simulate_rr(base, quantum)
                algoname = f"Round Robin (q={quantum})"

            metrics = compute_metrics(base)
            svg = svg_gantt(timeline)
            ascii = ascii_gantt(timeline)

            context.update({
                "form": form,
                "algoname": algoname,
                "timeline": timeline,
                "svg": svg,
                "ascii": ascii,
                "per": metrics["per_process"],
                "overall": metrics["overall"],
                "procs": sorted(procs_in, key=lambda x: x["pid"]),
            })
        else:
            context["form"] = form
    return render(request, "sim/index.html", context)

def api_simulate(request: HttpRequest):
    """
    JSON API:
    POST { algo: 'fcfs'|'sjf'|'rr', quantum?: int, procs: [{pid,arrival,burst}] }
    → { timeline, per_process, overall }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    import json
    try:
        payload = json.loads(request.body.decode("utf-8"))
        algo = payload["algo"]
        quantum = int(payload.get("quantum") or 2)
        arr = payload["procs"]
        procs = [Process(p["pid"], int(p["arrival"]), int(p["burst"])) for p in arr]
        base = deep_copy_procs(procs)

        if algo == "fcfs":
            tl = simulate_fcfs(base)
        elif algo == "sjf":
            tl = simulate_sjf_nonpreemptive(base)
        elif algo == "rr":
            tl = simulate_rr(base, quantum)
        else:
            return JsonResponse({"error": "Unknown algo"}, status=400)

        m = compute_metrics(base)
        timeline = [{"start": s, "end": e, "pid": pid} for (s, e, pid) in tl]
        return JsonResponse({
            "timeline": timeline,
            "per_process": m["per_process"],
            "overall": m["overall"],
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
