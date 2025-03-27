import json
from pathlib import Path
from stats import chi_square_against_theory
import constants as c

base_dir = Path(__file__).parent
input_file = base_dir / "simulation_results.json"
output_file = base_dir / "REPORT.md"

with open(input_file, "r") as f:
    results = json.load(f)

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

    entropy = f"{data['stats']['entropy']:.3f}"

    # Format PMS/OD ratio
    pms_od = data["stats"]["pms_od_ratio"]
    if isinstance(pms_od, float) and pms_od == float("inf"):
        pms_od_str = "∞"
    elif pms_od == "Infinity":
        pms_od_str = "∞"
    else:
        pms_od_str = f"{float(pms_od):.3f}"

    chi_square_uniform = f"{data['stats']['chi_square_p_value']:.5f}"

    # Calculate chi-square against theoretical distributions
    chi_square_suliman = chi_square_against_theory(counts, c.SULIMAN_DISTRIBUTION)
    chi_square_fernando = chi_square_against_theory(
        counts, c.FERNANDO_VOGEL_DISTRIBUTION
    )

    chi_square_suliman_str = f"{chi_square_suliman:.5f}"
    chi_square_fernando_str = f"{chi_square_fernando:.5f}"

    markdown += f"| {p} | {q} | {entropy} | {pms_od_str} | {chi_square_uniform} | {chi_square_suliman_str} | {chi_square_fernando_str} |\n"

with open(output_file, "w") as f:
    f.write(markdown)
