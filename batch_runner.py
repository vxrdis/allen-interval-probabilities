import argparse
import json
import math
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

from tqdm import tqdm

import constants as c
from simulations import arSimulate
from stats import describe_global

DEFAULT_TRIALS = 1000
DEFAULT_OUTPUT = "sim_results.json"


class InfEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and not math.isfinite():
            return "Infinity" if obj > 0 else "-Infinity"
        elif isinstance(obj, timedelta):
            return str(obj)
        return super().default(obj)


def collect_stats(counts):
    refs = {
        "Uniform": describe_global(counts, c.UNIFORM_DISTRIBUTION),
        "Suliman": describe_global(counts, c.SULIMAN_DISTRIBUTION, smooth=True),
        "F-V": describe_global(counts, c.FERNANDO_VOGEL_DISTRIBUTION, smooth=True),
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
    summary = refs["Uniform"]

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


def run_batch(trials, pBorn, pDie, short=False, quiet=False, seed=None):
    if seed is not None:
        random.seed(seed)
        if not quiet:
            print(f"Using random seed: {seed}")

    start = time.time()
    timestamp = datetime.now().isoformat(timespec="seconds")
    results = {}

    if not quiet:
        print(f"Simulating with pBorn={pBorn}, pDie={pDie}, trials={trials}")

    counts = arSimulate(pBorn, pDie, trials)
    result = {"p": pBorn, "q": pDie, "stats": collect_stats(counts)}
    if not short:
        result["counts"] = {rel: counts.get(rel, 0) for rel in c.ALLEN_RELATIONS}
    results[f"{pBorn:.6f}_{pDie:.6f}"] = result

    duration = timedelta(seconds=int(time.time() - start))
    metadata = {
        "timestamp": timestamp,
        "duration": str(duration),
        "trials": trials,
        "pBorn": pBorn,
        "pDie": pDie,
        "runs": 1,
    }

    return results, metadata


def main():
    parser = argparse.ArgumentParser(description="Allen relation simulator")
    parser.add_argument(
        "--trials",
        type=int,
        default=DEFAULT_TRIALS,
        help=f"Number of trials to run (default: {DEFAULT_TRIALS})",
    )
    parser.add_argument(
        "--pBorn", type=float, required=True, help="Birth probability (p)"
    )
    parser.add_argument(
        "--pDie", type=float, required=True, help="Death probability (q)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT,
        help=f"Output file path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")
    parser.add_argument(
        "--short", action="store_true", help="Exclude raw counts in output"
    )
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    args = parser.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not args.quiet:
        print(
            f"Running simulation with p={args.pBorn}, q={args.pDie}, trials={args.trials}"
        )
        print(f"Output: {out_path}")

    results, metadata = run_batch(
        args.trials, args.pBorn, args.pDie, args.short, args.quiet, args.seed
    )

    with out_path.open("w") as f:
        json.dump(
            {"metadata": metadata, "results": results},
            f,
            indent=2,
            cls=InfEncoder,
            sort_keys=True,
        )

    if not args.quiet:
        print(f"\nDone in {metadata['duration']} — Saved to {out_path.name}")


if __name__ == "__main__":
    main()
