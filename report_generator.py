import json
import math
from pathlib import Path
from stats import chi_square_against_theory
import constants as c

base_dir = Path(__file__).parent
simulation_file = base_dir / "simulation_results.json"
composition_file = base_dir / "composition_results.json"
output_file = base_dir / "RESULTS.md"


def get_file_type(data):
    """Determine if the JSON data is from simulation or composition results"""
    first_key = next(iter(data))
    first_item = data[first_key]
    if "p" in first_item and "q" in first_item:
        return "simulation"
    elif "r1" in first_item and "r2" in first_item:
        return "composition"
    else:
        return "unknown"


def format_number(value, precision=3):
    if value is None:
        return "N/A"
    elif isinstance(value, str) and (value == "Infinity" or value == "-Infinity"):
        return "∞" if value == "Infinity" else "-∞"
    elif isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        elif math.isinf(value):
            return "∞" if value > 0 else "-∞"
        else:
            return f"{value:.{precision}f}"
    else:
        return str(value)


def generate_simulation_report(results):
    markdown = "# Allen Interval Relation Simulation Results\n\n"
    markdown += "| p | q | Entropy | PMS/OD Ratio | Chi-square Uniform | Chi-square Suliman | Chi-square Fernando-Vogel |\n"
    markdown += "|---|---|---------|-------------|--------------------|--------------------|--------------------------|\n"
    sorted_keys = sorted(
        results.keys(), key=lambda k: (float(k.split("_")[0]), float(k.split("_")[1]))
    )
    for key in sorted_keys:
        data = results[key]
        p = data["p"]
        q = data["q"]
        counts = data["counts"]
        entropy_value = data["stats"].get("entropy", float("nan"))
        entropy = format_number(entropy_value, precision=3)
        pms_od = data["stats"].get("pms_od_ratio", float("nan"))
        pms_od_str = format_number(pms_od, precision=3)
        chi_square_uniform_value = data["stats"].get("chi_square_p_value", float("nan"))
        chi_square_uniform = format_number(chi_square_uniform_value, precision=5)
        try:
            chi_square_suliman = chi_square_against_theory(
                counts, c.SULIMAN_DISTRIBUTION
            )
            chi_square_suliman_str = format_number(chi_square_suliman, precision=5)
        except Exception:
            chi_square_suliman_str = "NaN"
        try:
            chi_square_fernando = chi_square_against_theory(
                counts, c.FERNANDO_VOGEL_DISTRIBUTION
            )
            chi_square_fernando_str = format_number(chi_square_fernando, precision=5)
        except Exception:
            chi_square_fernando_str = "NaN"
        markdown += f"| {p} | {q} | {entropy} | {pms_od_str} | {chi_square_uniform} | {chi_square_suliman_str} | {chi_square_fernando_str} |\n"
    return markdown


def generate_composition_report(results):
    markdown = "# Allen Interval Composition Results\n\n"
    markdown += "| Relation 1 | Relation 2 | Entropy | PMS/OD Ratio | Chi-square Uniform | Total Count |\n"
    markdown += "|------------|------------|---------|-------------|--------------------|-------------|\n"
    sorted_keys = sorted(results.keys())
    for key in sorted_keys:
        data = results[key]
        r1 = data["r1"]
        r2 = data["r2"]
        total_count = data["total_count"]
        if total_count == 0:
            continue
        entropy_value = data["stats"].get("entropy", float("nan"))
        entropy = format_number(entropy_value, precision=3)
        pms_od = data["stats"].get("pms_od_ratio", float("nan"))
        pms_od_str = format_number(pms_od, precision=3)
        chi_square_uniform_value = data["stats"].get("chi_square_p_value", float("nan"))
        chi_square_uniform = format_number(chi_square_uniform_value, precision=5)
        markdown += f"| {r1} | {r2} | {entropy} | {pms_od_str} | {chi_square_uniform} | {total_count} |\n"
    return markdown


markdown_content = ""
if simulation_file.exists():
    with open(simulation_file, "r") as f:
        sim_results = json.load(f)
        if get_file_type(sim_results) == "simulation":
            markdown_content += generate_simulation_report(sim_results)
            markdown_content += "\n\n---\n\n"
if composition_file.exists():
    with open(composition_file, "r") as f:
        comp_results = json.load(f)
        if get_file_type(comp_results) == "composition":
            markdown_content += generate_composition_report(comp_results)
with open(output_file, "w") as f:
    f.write(markdown_content)
print(f"Combined report generated at {output_file}")
