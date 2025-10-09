# procsim/sim/forms.py
from django import forms

ALGO_CHOICES = [
    ("fcfs", "FCFS"),
    ("sjf", "SJF (Non-Preemptive)"),
    ("rr", "Round-Robin"),
]

class SimForm(forms.Form):
    algorithm = forms.ChoiceField(choices=ALGO_CHOICES, initial="fcfs")
    quantum = forms.IntegerField(min_value=1, initial=2, required=False,
                                 help_text="Used only for Round-Robin")
    inline_procs = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows":6, "placeholder":"pid,arrival,burst\nP1,0,5\nP2,2,3\nP3,4,2"}),
        help_text="One per line: pid,arrival,burst"
    )
    csv_file = forms.FileField(required=False)
    json_file = forms.FileField(required=False)

    def clean(self):
        cleaned = super().clean()
        algo = cleaned.get("algorithm")
        q = cleaned.get("quantum")
        if algo == "rr" and not q:
            self.add_error("quantum", "Quantum is required for Round-Robin.")

        # Parse processes from one of: csv, json, inline
        procs = []
        if cleaned.get("csv_file"):
            import csv, io
            f = cleaned["csv_file"].read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(f))
            for row in reader:
                procs.append({
                    "pid": str(row["pid"]).strip(),
                    "arrival": int(row["arrival"]),
                    "burst": int(row["burst"]),
                })
        elif cleaned.get("json_file"):
            import json
            data = cleaned["json_file"].read().decode("utf-8")
            arr = json.loads(data)
            for r in arr:
                procs.append({
                    "pid": str(r["pid"]).strip(),
                    "arrival": int(r["arrival"]),
                    "burst": int(r["burst"]),
                })
        else:
            txt = cleaned.get("inline_procs", "").strip()
            if txt:
                for line in txt.splitlines():
                    if not line.strip(): continue
                    pid, at, bt = [x.strip() for x in line.split(",")]
                    procs.append({"pid": pid, "arrival": int(at), "burst": int(bt)})

        if not procs:
            self.add_error("inline_procs", "Provide processes via inline, CSV, or JSON.")

        cleaned["procs"] = procs
        return cleaned
