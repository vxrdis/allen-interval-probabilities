import sys, json, math
from fractions import Fraction
from pathlib import Path
from constants import (
    ALLEN_RELATIONS,
    RELATION_NAMES,
    UNIFORM_DISTRIBUTION,
    FERNANDO_VOGEL_DISTRIBUTION,
    SULIMAN_DISTRIBUTION,
)
from stats import entropy, gini, js_divergence

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
    frac = Fraction(decimal).limit_denominator(30)
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


def calculate_global_stats(comp):
    """Calculate global statistics from composition data"""
    # Track global distribution of R3 outcomes across all compositions
    global_r3_counts = {}

    # For each pair of relations, extract the composition results
    for r1 in ALLEN_RELATIONS:
        if r1 not in comp:
            continue
        for r2 in ALLEN_RELATIONS:
            if r2 not in comp[r1]:
                continue
            cell = comp[r1][r2]
            if cell == "unobserved":
                continue

            # Add counts to global distribution
            for r3, item in cell.items():
                count = item["count"]
                global_r3_counts[r3] = global_r3_counts.get(r3, 0) + count

    # Calculate global distribution percentages
    global_total = sum(global_r3_counts.values())
    global_distribution = (
        {rel: count / global_total for rel, count in global_r3_counts.items()}
        if global_total > 0
        else {}
    )

    # Calculate metrics
    global_entropy = entropy(global_distribution)
    global_gini = gini(global_distribution)
    global_coverage = sum(1 for val in global_distribution.values() if val > 0)

    # Calculate JS divergence against theoretical models
    js_uniform = js_divergence(global_distribution, UNIFORM_DISTRIBUTION)
    js_fv = js_divergence(global_distribution, FERNANDO_VOGEL_DISTRIBUTION)
    js_suliman = js_divergence(global_distribution, SULIMAN_DISTRIBUTION)

    # Determine best fit model
    min_js = min(js_uniform, js_fv, js_suliman)
    if min_js == js_uniform:
        best_fit = "Uniform"
        best_fit_js = js_uniform
    elif min_js == js_fv:
        best_fit = "Fernando-Vogel"
        best_fit_js = js_fv
    else:
        best_fit = "Suliman"
        best_fit_js = js_suliman

    # Mode (most common relation)
    mode_relation = (
        max(global_distribution.items(), key=lambda x: x[1])[0]
        if global_distribution
        else None
    )

    return {
        "distribution": global_distribution,
        "raw_counts": global_r3_counts,
        "entropy": global_entropy,
        "gini": global_gini,
        "coverage": global_coverage,
        "js_uniform": js_uniform,
        "js_fv": js_fv,
        "js_suliman": js_suliman,
        "best_fit": best_fit,
        "best_fit_js": best_fit_js,
        "mode": mode_relation,
        "mode_name": (
            RELATION_NAMES.get(mode_relation, "Unknown") if mode_relation else "N/A"
        ),
    }


def generate_composition_report(data, output_path):
    meta = data.get("timestamp", "N/A").replace("T", " ")
    duration = data.get("duration", "N/A")
    trials = format_int(data.get("trials", "N/A"))
    valid = format_int(data.get("valid_runs", "N/A"))
    coverage = data.get("coverage", "N/A")
    pBorn = data.get("pBorn", "N/A")
    pDie = data.get("pDie", "N/A")
    comp = data.get("compositions", {})

    # Calculate global statistics
    global_stats = calculate_global_stats(comp)

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

    # Add global statistics section
    lines.extend(
        [
            "\n## Global R3 Distribution Statistics",
            "*Aggregated across all R1•R2 composition pairs*",
            "",
            f"- **Entropy:** `{format_number(global_stats['entropy'])}`",
            f"- **Gini Coefficient:** `{format_number(global_stats['gini'])}`",
            f"- **Coverage:** `{global_stats['coverage']} / 13` relations",
            "",
            "### Model Fit (Jensen-Shannon Divergence)",
            f"- **Uniform:** `{format_number(global_stats['js_uniform'])}`",
            f"- **Fernando-Vogel:** `{format_number(global_stats['js_fv'])}`",
            f"- **Suliman:** `{format_number(global_stats['js_suliman'])}`",
            f"- **Best Fit:** `{global_stats['best_fit']}` (JS = `{format_number(global_stats['best_fit_js'])}`)",
            "",
            f"### Most Common Result: `{global_stats['mode']}` - {global_stats['mode_name']}",
            "",
            "### Global Distribution",
            "| Relation | Name | Count | Probability |",
            "|----------|------|-------|------------|",
        ]
    )

    # Add sorted global distribution table
    sorted_relations = sorted(
        [
            (rel, global_stats["distribution"][rel], global_stats["raw_counts"][rel])
            for rel in global_stats["distribution"]
        ],
        key=lambda x: x[1],
        reverse=True,
    )

    for rel, prob, count in sorted_relations:
        name = RELATION_NAMES.get(rel, "Unknown")
        lines.append(
            f"| {rel} | {name} | {format_int(count)} | {format_percentage(prob * 100)}% |"
        )

    lines.extend(
        [
            "\n---\n",
            "## Composition Table",
            "<sub>Only showing compositions with multiple outcomes. Fractions are limited to denominators `≤ 30`.</sub>",
            "| r1 | r2 | Total | r3 Outcomes (rel → %) | ≈ Fractions |",
            "|----|----|-------|-----------------------|-------------|",
        ]
    )

    # Track the number of filtered rows
    total_compositions = 0
    multiple_outcome_compositions = 0

    for r1 in ALLEN_RELATIONS:
        if r1 not in comp:
            continue
        for r2 in ALLEN_RELATIONS:
            if r2 not in comp[r1]:
                continue
            cell = comp[r1][r2]
            if cell == "unobserved":
                continue

            total_compositions += 1
            total = sum(item["count"] for item in cell.values())

            outcome_items = [
                (r3, cell[r3]["percentage"]) for r3 in ALLEN_RELATIONS if r3 in cell
            ]

            # Skip rows with a single outcome (100% probability)
            if len(outcome_items) <= 1:
                continue

            multiple_outcome_compositions += 1

            outcomes = ", ".join(
                f"{r3} ({format_percentage(pct)}%)" for r3, pct in outcome_items
            )

            fraction_cell = ", ".join(
                percentage_to_fraction(pct) for _, pct in outcome_items
            )

            lines.append(
                f"| {r1} | {r2} | {format_int(total)} | {outcomes} | {fraction_cell} |"
            )

    # Add a summary after the table showing how many compositions were filtered
    lines.append(
        f"\n**Note:** Showing {multiple_outcome_compositions} of {total_compositions} compositions. {total_compositions - multiple_outcome_compositions} compositions with only one outcome were filtered out."
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Composition report saved as: {output_path.name}")


def main():
    base = Path(__file__).parent

    # Allow override via CLI args
    comp_file = Path(sys.argv[1]) if len(sys.argv) > 1 else base / DEFAULT_INPUT
    comp_out = Path(sys.argv[2]) if len(sys.argv) > 2 else base / DEFAULT_OUTPUT

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
