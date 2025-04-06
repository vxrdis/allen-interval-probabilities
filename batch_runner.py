import argparse
import json
import math
import time
from pathlib import Path
from itertools import product

from tqdm import tqdm

import constants as c
from simulations import arSimulate
from stats import describe_global

DEFAULT_TRIALS = 500
DEFAULT_OUTPUT = "sim_results.json"
DEFAULT_P_VALUES = [0.001, 0.01, 0.05, 0.1, 0.2, 0.5]


class InfEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and not math.isfinite():
            return "Infinity" if obj > 0 else "-Infinity"
        return super().default(obj)


def parse_p_values(raw):
    try:
        return [float(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid p-values format.")


def collect_stats(counts):
    refs = {
        "uniform": describe_global(counts),
        "suliman": describe_global(counts, c.SULIMAN_DISTRIBUTION),
        "fernando-vogel": describe_global(counts, c.FERNANDO_VOGEL_DISTRIBUTION),
    }

    best_fit = min(
        (
            (name, stats.get("js_divergence"))
            for name, stats in refs.items()
            if stats.get("js_divergence") is not None
        ),
        key=lambda x: x[1],
        default=(None, None),
    )[0]

    metrics = ["chi_square_theory", "kl_divergence", "js_divergence"]
    labels = ["chi2_p", "kl", "js"]

    summary = refs["uniform"]
    return {
        "best_fit": best_fit,
        "summary": {
            k: (
                round(summary.get(k, 0), 4)
                if k not in ["coverage", "mode"]
                else summary.get(k)
            )
            for k in ["entropy", "gini", "coverage", "mode", "stddev"]
        },
        "compare": {
            name: {
                short: (
                    round(stats.get(metric, 0), 4)
                    if stats.get(metric) is not None
                    else None
                )
                for short, metric in zip(labels, metrics)
            }
            for name, stats in refs.items()
        },
    }


def run_batch(trials, p_values, short=False, quiet=False):
    grid = list(product(p_values, repeat=2))
    results = {}

    for p, q in tqdm(grid, disable=quiet, desc="Simulating"):
        counts = arSimulate(p, q, trials)
        result = {"p": p, "q": q, "stats": collect_stats(counts)}
        if not short:
            result["counts"] = {rel: counts.get(rel, 0) for rel in c.ALLEN_RELATIONS}
        results[f"{p:.6f}_{q:.6f}"] = result

    return results


def main():
    parser = argparse.ArgumentParser(description="Run Allen interval simulations")
    parser.add_argument("--trials", type=int, help="Number of trials per simulation")
    parser.add_argument("--p-values", type=parse_p_values, help="Probability values")
    parser.add_argument(
        "--output", type=str, default=DEFAULT_OUTPUT, help="Output file"
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    parser.add_argument("--short", action="store_true", help="Omit raw counts")
    args = parser.parse_args()

    trials = args.trials or DEFAULT_TRIALS
    p_values = args.p_values or DEFAULT_P_VALUES
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not args.quiet:
        n = len(p_values)
        print(f"Running {n**2} simulations × {trials} trials each")
        print(f"Output: {out_path}")

    start = time.time()
    results = run_batch(trials, p_values, args.short, args.quiet)

    with out_path.open("w") as f:
        json.dump(results, f, indent=2, cls=InfEncoder)

    if not args.quiet:
        print(f"\nDone in {time.time()-start:.2f}s — Saved to {out_path.name}")


if __name__ == "__main__":
    main()
