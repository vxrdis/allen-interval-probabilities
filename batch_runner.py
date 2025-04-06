import argparse
import json
import time
from pathlib import Path
from itertools import product

from tqdm import tqdm

import constants as c
from simulations import arSimulate
from stats import describe_global

DEFAULT_TRIALS = 500
DEFAULT_OUTPUT = "sim_results.json"
DEFAULT_PROB_VALUES = [0.001, 0.01, 0.05, 0.1, 0.2, 0.5]


class InfEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and not obj.isfinite():
            return "Infinity" if obj > 0 else "-Infinity"
        return super().default(obj)


def parse_probabilities(raw: str) -> list[float]:
    try:
        return [float(x.strip()) for x in raw.split(",") if x.strip()]
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Invalid --p-values. Use comma-separated floats."
        )


def collect_stats(counts: dict) -> dict:
    refs = {
        "uniform": describe_global(counts),
        "suliman": describe_global(counts, c.SULIMAN_DISTRIBUTION),
        "fernando-vogel": describe_global(counts, c.FERNANDO_VOGEL_DISTRIBUTION),
    }

    best_fit = min(
        (
            (name, stats["js_divergence"])
            for name, stats in refs.items()
            if stats["js_divergence"] is not None
        ),
        key=lambda x: x[1],
        default=(None, None),
    )[0]

    def clean(d):
        return {
            "chi2_p": (
                round(d["chi_square_theory"], 4)
                if d.get("chi_square_theory") is not None
                else None
            ),
            "kl": (
                round(d["kl_divergence"], 4)
                if d.get("kl_divergence") is not None
                else None
            ),
            "js": (
                round(d["js_divergence"], 4)
                if d.get("js_divergence") is not None
                else None
            ),
        }

    summary = refs["uniform"]  # same values for entropy, gini, etc.
    return {
        "best_fit": best_fit,
        "summary": {
            "entropy": round(summary["entropy"], 4),
            "gini": round(summary["gini"], 4),
            "coverage": summary["coverage"],
            "mode": summary["mode"],
            "stddev": round(summary["stddev"], 4),
        },
        "compare": {k: clean(v) for k, v in refs.items()},
    }


def run_batch(trials: int, p_values: list[float], short=False, quiet=False) -> dict:
    grid = list(product(p_values, repeat=2))
    results = {}
    for p, q in tqdm(grid, disable=quiet, desc="Simulating"):
        counts_raw = arSimulate(p, q, trials)
        key = f"{p}_{q}"
        counts_ordered = {rel: counts_raw.get(rel, 0) for rel in c.ALLEN_RELATIONS}
        result = {
            "p": p,
            "q": q,
            "stats": collect_stats(counts_raw),
        }
        if not short:
            result["counts"] = counts_ordered
        results[key] = result
    return results


def write_output(data: dict, path: Path) -> None:
    with path.open("w") as f:
        json.dump(data, f, indent=2, cls=InfEncoder)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int)
    parser.add_argument("--p-values", type=parse_probabilities)
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--short", action="store_true")
    args = parser.parse_args()

    trials = args.trials or DEFAULT_TRIALS
    p_values = args.p_values or DEFAULT_PROB_VALUES
    out_path = Path(args.output)

    if not args.quiet:
        n = len(p_values)
        print(f"Running {n * n} simulations of {trials} trials each...")
        print(f"Output: {out_path}")

    start = time.time()
    results = run_batch(trials, p_values, short=args.short, quiet=args.quiet)
    write_output(results, out_path)

    if not args.quiet:
        print(f"\nDone in {time.time() - start:.2f}s. Saved to {out_path}")


if __name__ == "__main__":
    main()
