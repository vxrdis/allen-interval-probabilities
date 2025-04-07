import json, math
from pathlib import Path

DEFAULT_INPUT, DEFAULT_OUTPUT = "sim_results.json", "SIM_RESULTS.md"


def format_number(val, digits=4):
    if val is None:
        return "N/A"
    if isinstance(val, float):
        if math.isnan(val):
            return "NaN"
        if math.isinf(val):
            return "∞" if val > 0 else "-∞"
        return f"{val:.{digits}f}"
    return str(val)


def generate_simulation_report(data, output_path):
    meta, results = data.get("metadata", {}), data.get("results", {})

    lines = [
        "# Simulation Results",
        f"- **Generated:** `{meta.get('timestamp', 'N/A').replace('T', ' ')}`",
        f"- **Duration:** `{meta.get('duration', 'N/A')}`",
        f"- **Trials per (p, q):** `{meta.get('trials', 'N/A')}`",
        f"- **Grid Size:** `{meta.get('runs', 'N/A')} pairs`",
        "\n---\n",
        "| p | q | Entropy | Gini | Stddev | Coverage | Mode | Best Fit | JS (Uniform) | JS (Suliman) | JS (F&#8209;V) |",
        "|----|----|---------|-------|--------|-----------|------|-----------|--------------|--------------|----------|",
    ]

    for key in sorted(results.keys()):
        entry = results[key]
        p, q = entry.get("p", 0), entry.get("q", 0)
        stats = entry.get("stats", {})
        summary = stats.get("summary", {})
        compare = stats.get("compare", {})

        lines.append(
            f"| {p:.3f} | {q:.3f} "
            f"| {format_number(summary.get('entropy'))} "
            f"| {format_number(summary.get('gini'))} "
            f"| {format_number(summary.get('stddev'))} "
            f"| {summary.get('coverage', 'N/A')} "
            f"| {summary.get('mode', 'N/A')} "
            f"| {stats.get('best_fit', 'N/A')} "
            f"| {format_number(compare.get('Uniform', {}).get('js'))} "
            f"| {format_number(compare.get('Suliman', {}).get('js'))} "
            f"| {format_number(compare.get('F-V', {}).get('js'))} |"
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Simulation report saved as: {output_path.name}")


def main():
    base = Path(__file__).parent
    sim_file, sim_out = base / DEFAULT_INPUT, base / DEFAULT_OUTPUT

    if not sim_file.exists():
        print(f"File not found: {sim_file}")
        return

    try:
        with sim_file.open(encoding="utf-8") as f:
            data = json.load(f)
        generate_simulation_report(data, sim_out)
    except Exception as e:
        print(f"Failed to generate report: {e}")


if __name__ == "__main__":
    main()
