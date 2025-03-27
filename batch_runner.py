import json
from pathlib import Path
from simulations import arSimulate
from stats import describe


class InfEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and (obj == float("inf") or obj == float("-inf")):
            return "Infinity" if obj > 0 else "-Infinity"
        return super().default(obj)


probabilities = [0.001, 0.01, 0.05, 0.1, 0.2, 0.5]

results = {}

for p in probabilities:
    for q in probabilities:
        print(f"Running simulation with p={p}, q={q}...")
        counts = arSimulate(p, q, 5000)
        stats_summary = describe(counts)
        key = f"{p}_{q}"
        results[key] = {"p": p, "q": q, "counts": counts, "stats": stats_summary}

output_file = Path(__file__).parent / "simulation_results.json"
with open(output_file, "w") as f:
    json.dump(results, f, indent=2, cls=InfEncoder)

print(f"Simulations complete. Results saved to {output_file}")
