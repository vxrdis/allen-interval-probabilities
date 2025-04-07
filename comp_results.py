import json, math
from fractions import Fraction
from pathlib import Path
from constants import ALLEN_RELATIONS

DEFAULT_INPUT, DEFAULT_OUTPUT = "comp_results.json", "COMP_RESULTS.md"


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


def format_percentage(val, digits=2):
    if val is None:
        return "N/A"
    if isinstance(val, float):
        result = f"{val:.{digits}f}".rstrip("0").rstrip(".")
        return result or "0"
    return str(val)


def format_int(val):
    try:
        return f"{int(val)}"
    except Exception:
        return str(val)


def get_missing_compositions(comp):
    missing = []
    for r1 in ALLEN_RELATIONS:
        for r2 in ALLEN_RELATIONS:
            if r1 not in comp or r2 not in comp[r1] or comp[r1][r2] == "unobserved":
                missing.append(f"`{r1}` ∘ `{r2}`")
    return missing


def percentage_to_fraction(percentage):
    if percentage == 100:
        return "1"
    decimal = percentage / 100
    frac = Fraction(decimal).limit_denominator(20)
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


def generate_composition_report(data, output_path):
    meta = data.get("timestamp", "N/A").replace("T", " ")
    duration = data.get("duration", "N/A")
    trials = format_int(data.get("trials", "N/A"))
    valid = format_int(data.get("valid_runs", "N/A"))
    coverage = data.get("coverage", "N/A")
    pBorn = data.get("pBorn", "N/A")
    pDie = data.get("pDie", "N/A")
    comp = data.get("compositions", {})

    missing_compositions = get_missing_compositions(comp)
    missing_count = len(missing_compositions)

    missing_section = []
    if missing_count > 0:
        missing_section = [
            "<details>",
            f"<summary>⚠ Missing compositions: {missing_count}</summary>",
            "",
            "\n".join(f"1. {item}" for item in missing_compositions),
            "</details>",
        ]

    lines = [
        "# Composition Results",
        f"- **Generated:** `{meta}`",
        f"- **Duration:** `{duration}`",
        f"- **Trials:** `{trials}`",
        f"- **Valid Runs:** `{valid}`",
        f"- **Coverage:** `{coverage} / 169`",
        f"- **Birth Probability (p):** `{pBorn}`",
        f"- **Death Probability (q):** `{pDie}`",
    ]

    if missing_section:
        lines.extend(missing_section)

    lines.extend(
        [
            "\n---\n",
            "<sub>In the fractions column, `-` indicates a single outcome with 100% probability. Fractions are limited to denominators `≤ 20`.</sub>",
            "| r1 | r2 | Total | r3 Outcomes (rel → %) | ≈ Fractions |",
            "|----|----|-------|-----------------------|-------------|",
        ]
    )

    for r1 in ALLEN_RELATIONS:
        if r1 not in comp:
            continue
        for r2 in ALLEN_RELATIONS:
            if r2 not in comp[r1]:
                continue
            cell = comp[r1][r2]
            if cell == "unobserved":
                continue
            total = sum(item["count"] for item in cell.values())

            outcome_items = [
                (r3, cell[r3]["percentage"]) for r3 in ALLEN_RELATIONS if r3 in cell
            ]
            outcomes = ", ".join(
                f"{r3} ({format_percentage(pct)}%)" for r3, pct in outcome_items
            )

            fraction_cell = (
                ", ".join(percentage_to_fraction(pct) for _, pct in outcome_items)
                if len(outcome_items) > 1
                else "-"
            )
            lines.append(
                f"| {r1} | {r2} | {format_int(total)} | {outcomes} | {fraction_cell} |"
            )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Composition report saved as: {output_path.name}")


def main():
    base = Path(__file__).parent
    comp_file, comp_out = base / DEFAULT_INPUT, base / DEFAULT_OUTPUT

    if not comp_file.exists():
        print(f"File not found: {comp_file}")
        return

    try:
        with comp_file.open(encoding="utf-8") as f:
            data = json.load(f)
        generate_composition_report(data, comp_out)
    except Exception as e:
        print(f"Failed to generate report: {e}")


if __name__ == "__main__":
    main()
