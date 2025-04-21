import argparse
import json
import math
import random
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from tqdm import tqdm

from constants import ALLEN_RELATIONS
from simulations import updateState, arCode

DEFAULT_TRIALS = 1000000
DEFAULT_P_BORN = 0.5
DEFAULT_P_DIE = 0.5
DEFAULT_OUTPUT_FILE = "comp_results.json"


class InfEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and not math.isfinite():
            return "Infinity" if obj > 0 else "-Infinity"
        elif isinstance(obj, timedelta):
            return str(obj)
        return super().default(obj)


def project(history, i, j):
    out = [pair := [history[0][i], history[0][j]]]
    for state in history[1:]:
        curr = [state[i], state[j]]
        if curr != pair:
            out.append(curr)
            pair = curr
    return out


def generate_valid_triples(p_born, p_die, trials, limit=None, quiet=False):
    if not 0 <= p_born <= 1 or not 0 <= p_die <= 1:
        raise ValueError(
            f"Probabilities must be in [0, 1] range: pBorn={p_born}, pDie={p_die}"
        )

    runs = []
    max_runs = limit or trials
    pbar = tqdm(total=max_runs, disable=quiet, desc="Simulating")

    for _ in range(trials):
        if len(runs) >= max_runs:
            break

        hist = [[0, 0, 0]]
        while hist[-1] != [2, 2, 2]:
            last = hist[-1]
            next_state = [updateState(last[i], p_born, p_die) for i in range(3)]
            if next_state != last:
                hist.append(next_state)

        r12 = arCode(project(hist, 0, 1))
        r23 = arCode(project(hist, 1, 2))
        r13 = arCode(project(hist, 0, 2))

        if None not in (r12, r23, r13):
            runs.append((r12, r23, r13))
            pbar.update(1)

    pbar.close()

    if not runs:
        raise RuntimeError(f"No valid triples were generated after {trials} attempts.")

    return runs


def build_composition_table(runs):
    table = {
        r1: {r2: defaultdict(int) for r2 in ALLEN_RELATIONS} for r1 in ALLEN_RELATIONS
    }
    for r1, r2, r3 in runs:
        table[r1][r2][r3] += 1
    return table


def summarise_compositions(table, p_born, p_die, trials, metadata):
    compositions = {}
    for r1 in table:
        compositions[r1] = {}
        for r2 in table[r1]:
            counts = table[r1][r2]
            total = sum(counts.values())
            if total == 0:
                compositions[r1][r2] = "unobserved"
            else:
                compositions[r1][r2] = {
                    r3: {
                        "count": counts[r3],
                        "percentage": round((counts[r3] / total) * 100, 2),
                    }
                    for r3 in counts
                    if counts[r3] > 0
                }

    coverage = sum(
        1
        for r1 in compositions
        for r2 in compositions[r1]
        if compositions[r1][r2] != "unobserved"
    )

    return {
        "pBorn": p_born,
        "pDie": p_die,
        "trials": trials,
        "coverage": coverage,
        "timestamp": metadata["timestamp"],
        "duration": metadata["duration"],
        "valid_runs": metadata["valid_runs"],
        "compositions": compositions,
    }


def run(p_born, p_die, trials, limit=None, quiet=False, seed=None):
    if seed is not None:
        random.seed(seed)
        if not quiet:
            print(f"Using random seed: {seed}")

    start = time.time()
    timestamp = datetime.now().isoformat(timespec="seconds")

    if not quiet:
        print(
            f"Running {trials} simulations with pBorn={p_born}, pDie={p_die}"
            + (f" (limited to {limit} valid runs)" if limit else "")
        )

    runs = generate_valid_triples(p_born, p_die, trials, limit, quiet)

    table = build_composition_table(runs)
    duration = timedelta(seconds=int(time.time() - start))

    metadata = {"timestamp": timestamp, "duration": duration, "valid_runs": len(runs)}
    stats = summarise_compositions(table, p_born, p_die, trials, metadata)

    if not quiet:
        print(f"Completed in {duration}")

    return stats


def main():
    parser = argparse.ArgumentParser(description="Allen relation composition simulator")
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    parser.add_argument("--pBorn", type=float, default=DEFAULT_P_BORN)
    parser.add_argument("--pDie", type=float, default=DEFAULT_P_DIE)
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_FILE)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    if args.limit is None:
        args.limit = args.trials

    stats = run(args.pBorn, args.pDie, args.trials, args.limit, args.quiet, args.seed)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w") as f:
        json.dump(stats, f, indent=2, cls=InfEncoder, sort_keys=True)

    if not args.quiet:
        total_entries = sum(
            len(v)
            for r1, subdict in stats["compositions"].items()
            for r2, v in subdict.items()
            if v != "unobserved"
        )
        print(
            f"\nSaved to {out_path.name} — {stats['coverage']} out of 169 possible compositions observed"
            f" with {total_entries} composition entries (r1 ◦ r2 → r3)"
        )


if __name__ == "__main__":
    main()
