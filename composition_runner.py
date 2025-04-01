import json
import argparse
import random
from pathlib import Path
import constants as c
from intervals import gen, get_relation
from stats import describe
from itertools import product


class InfEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and (obj == float("inf") or obj == float("-inf")):
            return "Infinity" if obj > 0 else "-Infinity"
        return super().default(obj)


def preprocess_infinity_values(data):
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if isinstance(value, float) and (
                value == float("inf") or value == float("-inf")
            ):
                data[key] = "Infinity" if value > 0 else "-Infinity"
            elif isinstance(value, (dict, list)):
                preprocess_infinity_values(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, float) and (
                item == float("inf") or item == float("-inf")
            ):
                data[i] = "Infinity" if item > 0 else "-Infinity"
            elif isinstance(item, (dict, list)):
                preprocess_infinity_values(item)
    return data


def generate_interval_pair(relation):
    noise = lambda: random.uniform(-0.5, 0.5)  # increased from ± 0.2
    base = random.uniform(0, 10)  # expanded from 0–5

    if relation == c.BEFORE:
        x_start = base + noise()
        x_end = x_start + 1 + noise()
        y_start = x_end + 0.5 + noise()
        y_end = y_start + 1 + noise()

    elif relation == c.MEETS:
        x_start = base + noise()
        x_end = x_start + 1 + noise()
        y_start = x_end
        y_end = y_start + 1 + noise()

    elif relation == c.OVERLAPS:
        x_start = base + noise()
        y_start = x_start + 0.5 + noise()
        x_end = y_start + 0.5 + noise()
        y_end = x_end + 0.5 + noise()

    elif relation == c.CONTAINS:
        x_start = base + noise()
        y_start = x_start + 0.5 + noise()
        y_end = y_start + 0.5 + noise()
        x_end = y_end + 0.5 + noise()

    elif relation == c.DURING:
        y_start = base + noise()
        x_start = y_start + 0.5 + noise()
        x_end = x_start + 0.5 + noise()
        y_end = x_end + 0.5 + noise()

    elif relation == c.FINISHES:
        y_start = base + noise()
        x_start = y_start + 0.5 + noise()
        x_end = y_end = x_start + 1 + noise()

    elif relation == c.FINISHED_BY:
        x_start = base + noise()
        y_start = x_start + 0.5 + noise()
        x_end = y_end = y_start + 1 + noise()

    elif relation == c.STARTS:
        x_start = y_start = base + noise()
        x_end = x_start + 0.5 + noise()
        y_end = x_end + 0.5 + noise()

    elif relation == c.STARTED_BY:
        x_start = y_start = base + noise()
        y_end = y_start + 0.5 + noise()
        x_end = y_end + 0.5 + noise()

    elif relation == c.EQUALS:
        x_start = y_start = base + noise()
        x_end = y_end = x_start + 1 + noise()

    elif relation == c.MET_BY:
        y_start = base + noise()
        y_end = y_start + 1 + noise()
        x_start = y_end
        x_end = x_start + 1 + noise()

    elif relation == c.OVERLAPPED_BY:
        y_start = base + noise()
        x_start = y_start + 0.5 + noise()
        y_end = x_start + 0.5 + noise()
        x_end = y_end + 0.5 + noise()

    elif relation == c.AFTER:
        y_start = base + noise()
        y_end = y_start + 1 + noise()
        x_start = y_end + 0.5 + noise()
        x_end = x_start + 1 + noise()

    else:
        raise ValueError(f"Unknown relation: {relation}")

    return (x_start, x_end), (y_start, y_end)


def generate_targeted_intervals(r1, r2, max_attempts=100):  # increased from 10
    for attempt in range(max_attempts):
        (x_start, x_end), (y_start, y_end) = generate_interval_pair(r1)

        (temp_y_start, temp_y_end), (z_start, z_end) = generate_interval_pair(r2)

        y_duration = y_end - y_start
        temp_y_duration = temp_y_end - temp_y_start
        scale_factor = y_duration / temp_y_duration

        offset = y_start - temp_y_start

        micro_noise = lambda: random.uniform(-0.05, 0.05)

        z_start = (z_start - temp_y_start) * scale_factor + y_start + micro_noise()
        z_end = (z_end - temp_y_start) * scale_factor + y_start + micro_noise()

        actual_r1 = get_relation(x_start, x_end, y_start, y_end)
        actual_r2 = get_relation(y_start, y_end, z_start, z_end)
        r3 = get_relation(x_start, x_end, z_start, z_end)

        if actual_r1 == r1 and actual_r2 == r2:
            return ((x_start, x_end), (y_start, y_end), (z_start, z_end)), (
                actual_r1,
                actual_r2,
                r3,
            )
        else:
            print(
                f"Attempt {attempt+1}: Generated relations ({actual_r1},{actual_r2}) "
                f"don't match requested relations ({r1},{r2})"
            )

    error_msg = (
        f"Failed to generate intervals with relations ({r1},{r2}) "
        f"after {max_attempts} attempts"
    )
    raise ValueError(error_msg)


def simulate_compositions(trials_per_pair=500):
    compositions = {}

    for r1, r2 in product(c.ALLEN_RELATIONS, c.ALLEN_RELATIONS):
        comp_key = f"{r1}_{r2}"
        print(f"Simulating relation pair: {r1}, {r2}...")

        compositions[comp_key] = {
            "counts": {rel: 0 for rel in c.ALLEN_RELATIONS},
            "total_count": 0,
            "r1": r1,
            "r2": r2,
        }

        successful_trials = 0
        attempts = 0
        max_attempts = trials_per_pair * 3

        while successful_trials < trials_per_pair and attempts < max_attempts:
            attempts += 1
            try:
                intervals, relations = generate_targeted_intervals(r1, r2)
                successful_trials += 1

                actual_r1, actual_r2, r3 = relations

                assert actual_r1 == r1, f"Expected r1={r1}, got {actual_r1}"
                assert actual_r2 == r2, f"Expected r2={r2}, got {actual_r2}"

                compositions[comp_key]["counts"][r3] += 1
                compositions[comp_key]["total_count"] += 1

            except ValueError as e:
                if attempts % 50 == 0:
                    print(f"  Warning: {str(e)}")
                continue

        if successful_trials < trials_per_pair:
            print(
                f"  Warning: Only completed {successful_trials}/{trials_per_pair} trials for {r1}_{r2}"
            )
        else:
            print(f"  Completed {successful_trials} trials for {r1}_{r2}")

    return compositions


def run_batch_simulation(trials_per_pair=500):
    print(
        f"Running systematic composition simulation with {trials_per_pair} trials per relation pair..."
    )
    compositions = simulate_compositions(trials_per_pair)

    all_results = {}
    for comp_key, data in compositions.items():
        stats_summary = describe(data["counts"])

        all_results[comp_key] = {
            "r1": data["r1"],
            "r2": data["r2"],
            "counts": data["counts"],
            "total_count": data["total_count"],
            "normalized": {
                rel: count / data["total_count"]
                for rel, count in data["counts"].items()
                if data["total_count"] > 0
            },
            "stats": stats_summary,
        }

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Simulate Allen interval relation compositions"
    )
    parser.add_argument(
        "--trials", type=int, default=500, help="Number of trials per relation pair"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="composition_results.json",
        help="Output JSON file path",
    )

    args = parser.parse_args()

    results = run_batch_simulation(args.trials)
    results = preprocess_infinity_values(results)

    total_compositions = sum(data["total_count"] for data in results.values())
    total_combinations = len(results)

    print(f"Simulation complete!")
    print(
        f"Generated {total_compositions} composition instances across {total_combinations} relation pairs"
    )
    print(f"Parameters: {args.trials} trials per relation pair")

    output_file = Path(__file__).parent / args.output
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, cls=InfEncoder)

    print(f"Results saved to {output_file}")


def run_examples():
    print("\nExample of targeted interval generation:")
    intervals, relations = generate_targeted_intervals("m", "o")
    print(f"Intervals: {intervals}")
    print(f"Relations: {relations}")


if __name__ == "__main__":
    main()
    # run_examples()
