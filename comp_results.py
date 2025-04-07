import json
import math
from pathlib import Path

DEFAULT_INPUT, DEFAULT_OUTPUT = "comp_results.json", "COMP_RESULTS.md"


def format_number(val, digits=4):
    if val is None:
        return "N/A"
    if isinstance(val, str):
        return val
    if isinstance(val, float):
        if math.isnan(val):
            return "NaN"
        elif math.isinf(val):
            return "∞" if val > 0 else "-∞"
        return f"{val:.{digits}f}"
    return str(val)


def generate_composition_report(comp_json, output_path):
    lines = [
        "# Composition Results",
        f"**Generated:** {comp_json.get('timestamp', 'N/A')}",
        f"**Duration:** {comp_json.get('duration', 'N/A')}",
        f"**Trials:** {comp_json.get('trials', 'N/A')}",
        f"**Valid Runs:** {comp_json.get('valid_runs', 'N/A')}",
        f"**Coverage:** {comp_json.get('coverage', 'N/A')} / 169",
        f"**Birth Probability (p):** {comp_json.get('pBorn', 'N/A')}",
        f"**Death Probability (q):** {comp_json.get('pDie', 'N/A')}",
        "\n---\n",
        "| r1 | r2 | Total | r3 Outcomes (All %) |",
        "|----|----|-------|---------------------|",
    ]

    comp = comp_json.get("compositions", {})
    for r1 in sorted(comp.keys()):
        for r2 in sorted(comp[r1].keys()):
            val = comp[r1][r2]
            if val == "unobserved":
                continue
            total = sum(item["count"] for item in val.values())
            all_str = ", ".join(
                f"{k} ({float(v['percentage']):.2f}%)"
                for k, v in sorted(val.items(), key=lambda x: -x[1]["count"])
            )
            lines.append(f"| {r1} | {r2} | {total} | {all_str} |")

    output_path.write_text("\n".join(lines))
    print(f"Composition report written to {output_path.name}")


def main():
    base = Path(__file__).parent
    comp_file = base / DEFAULT_INPUT
    comp_out = base / DEFAULT_OUTPUT

    if comp_file.exists():
        try:
            with open(comp_file) as f:
                generate_composition_report(json.load(f), comp_out)
        except Exception as e:
            print(f"Error generating composition report: {e}")


if __name__ == "__main__":
    main()
