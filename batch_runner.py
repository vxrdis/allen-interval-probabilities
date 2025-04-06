import json
from pathlib import Path
from simulations import arSimulate
from stats import describe_global


class InfEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and (obj == float("inf") or obj == float("-inf")):
            return "Infinity" if obj > 0 else "-Infinity"
        return super().default(obj)


# Grid of birth/death probabilities to explore
probabilities = [0.001, 0.01, 0.05, 0.1, 0.2, 0.5]
results = {}

for p in probabilities:
    for q in probabilities:
        print(f"Simulating p={p:.3f}, q={q:.3f}...")
        counts = arSimulate(p, q, 5000)
        stats_summary = describe_global(counts)
        key = f"{p}_{q}"
        results[key] = {
            "p": p,
            "q": q,
            "counts": counts,
            "stats": stats_summary,
        }

# Save results to JSON file
output_path = Path(__file__).parent / "simulation_results.json"
with output_path.open("w") as f:
    json.dump(results, f, indent=2, cls=InfEncoder)

print(f"\n✅ Batch simulations complete. Results saved to: {output_path}")
