"""
Parameter Surface Visualization for Allen's Interval Algebra

This module provides functions to generate and visualize 3D surface plots showing how
the birth probability (pBorn) and death probability (pDie) parameters affect various metrics
in Allen's interval algebra simulations.

The visualizations help explore the parameter space to understand:
1. How specific relation probabilities vary with birth/death parameters
2. How uniformity test statistics (chi-square) change across parameter combinations

These plots assist in identifying regions of parameter space with interesting behaviors,
such as uniform distributions or parameter combinations that favor certain relations.
"""

import time
import numpy as np
from dash import dcc, html
import plotly.graph_objects as go

# Import from our modules
from constants import ALLEN_RELATION_ORDER, get_relation_name
from simulations import simulateRed, arCode, set_random_seed
import scipy.stats as stats

# Import shared utilities
from shared_utils import calculate_shannon_entropy, normalize_counts
from analysis_utils import (
    test_uniform_distribution,
    calculate_expected_frequencies,
    analyze_distribution,
)


def generate_parameter_surface_data(
    p_values, selected_relation=None, trials_per_point=500, print_results=False
):
    """
    Generate simulation data across a grid of birth/death probability parameters.

    This function runs simulations for multiple combinations of pBorn and pDie,
    collecting both the probability of a selected relation and statistical metrics
    at each grid point.

    Args:
        p_values: List of probability values to use for both pBorn and pDie
        selected_relation: The specific Allen relation to track (default: 'e' for equals)
        trials_per_point: Number of simulation trials for each parameter combination
        print_results: Whether to print uniformity test results for each point

    Returns:
        Dictionary with grid data for 3D surface plotting
    """
    # Default to equals relation if none specified
    if selected_relation is None:
        selected_relation = "e"

    grid_size = len(p_values)

    # Initialize arrays for storing various metrics
    probability_grid = np.zeros((grid_size, grid_size))
    chi2_grid = np.zeros((grid_size, grid_size))
    p_value_grid = np.zeros((grid_size, grid_size))
    entropy_grid = np.zeros((grid_size, grid_size))

    # Track computation progress and time
    total_points = grid_size * grid_size
    completed_points = 0
    start_time = time.time()

    # Run simulations for all parameter combinations
    for i, pBorn in enumerate(p_values):
        for j, pDie in enumerate(p_values):
            # Set a fixed random seed for reproducibility at each grid point
            set_random_seed()

            # Run simulation for this parameter combination
            histories = simulateRed(pBorn, pDie, trials_per_point)

            # Count occurrences of each relation
            counts = {rel: 0 for rel in ALLEN_RELATION_ORDER}
            for history in histories:
                relation = arCode(history)
                if relation:
                    counts[relation] += 1

            # Calculate total and probabilities
            total_count = sum(counts.values())
            if total_count > 0:
                # Calculate probabilities for all relations
                probs = normalize_counts(counts)

                # Track probability of the selected relation
                probability_grid[i, j] = probs[selected_relation]

                # Calculate chi-square statistic for uniformity test
                observed = [counts[rel] for rel in ALLEN_RELATION_ORDER]

                # Calculate entropy of the distribution
                prob_values = list(probs.values())
                entropy = calculate_shannon_entropy(prob_values)
                entropy_grid[i, j] = entropy

                # Handle case where not enough data for chi-square test
                if total_count >= 13:  # At least one expected sample per category
                    test_results = test_uniform_distribution(counts)
                    chi2_grid[i, j] = test_results["chi2"]
                    p_value_grid[i, j] = test_results["p_value"]

                    if print_results:
                        print(
                            f"Point ({pBorn:.3f}, {pDie:.3f}): chi²={test_results['chi2']:.4f}, p={test_results['p_value']:.6f} - "
                            + f"{test_results['conclusion']}"
                        )

            # Track progress
            completed_points += 1
            if completed_points % 5 == 0 or completed_points == total_points:
                print(
                    f"Progress: {completed_points}/{total_points} points computed ({completed_points/total_points*100:.1f}%)"
                )

    # Calculate elapsed time
    elapsed_time = time.time() - start_time

    return {
        "pBorn_values": p_values,
        "pDie_values": p_values,
        "probability_grid": probability_grid,
        "chi2_grid": chi2_grid,
        "p_value_grid": p_value_grid,
        "entropy_grid": entropy_grid,
        "selected_relation": selected_relation,
        "computation_time": elapsed_time,
        "trials_per_point": trials_per_point,
    }


def create_3d_surface_plot(surface_data, metric_type="probability"):
    """
    Create a 3D surface plot visualizing parameter effects on Allen relations.

    Args:
        surface_data: Output from generate_parameter_surface_data
        metric_type: Type of data to visualize - "probability", "chi2", or "entropy"

    Returns:
        Plotly Figure object for 3D surface visualization
    """
    # Extract data from the input
    pBorn_values = surface_data["pBorn_values"]
    pDie_values = surface_data["pDie_values"]
    selected_relation = surface_data["selected_relation"]

    # Select data and configure visualization based on the requested metric
    if metric_type == "probability":
        z_data = surface_data["probability_grid"]
        rel_name = get_relation_name(selected_relation)
        title = f"Probability of Relation '{selected_relation}' ({rel_name})"
        color_scale = "Viridis"  # Blue-green-yellow for probability
        z_label = "Probability"
        colorbar_title = "Probability"

    elif metric_type == "entropy":
        z_data = surface_data["entropy_grid"]
        title = "Shannon Entropy of Relation Distribution"
        color_scale = "Plasma"  # Yellow-pink for entropy
        z_label = "Entropy (bits)"
        colorbar_title = "Entropy (bits)"

    else:  # chi-square statistic
        z_data = surface_data["chi2_grid"]
        title = "Chi-Square Statistic (Uniformity Test)"
        color_scale = "Inferno"  # Yellow-red-black for chi-square
        z_label = "Chi² Value"
        colorbar_title = "Chi² Statistic"

    # Create the 3D surface figure
    fig = go.Figure(
        data=[
            go.Surface(
                x=pBorn_values,
                y=pDie_values,
                z=z_data,
                colorscale=color_scale,
                colorbar=dict(title=colorbar_title),
            )
        ]
    )

    # Update figure layout with proper labels and settings
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="Birth Probability (pBorn)",
            yaxis_title="Death Probability (pDie)",
            zaxis_title=z_label,
            # Set initial camera position for better viewing angle
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
            # Add aspect ratio to avoid distortion
            aspectratio=dict(x=1, y=1, z=0.7),
        ),
        # Add margin for better spacing
        margin=dict(l=65, r=50, b=65, t=90),
        height=700,
        width=900,
    )

    # Add hover template for better interaction
    fig.update_traces(
        hovertemplate=(
            "pBorn: %{x:.3f}<br>"
            + "pDie: %{y:.3f}<br>"
            + f"{z_label}: %{{z:.4f}}<br>"
            + "<extra></extra>"
        )
    )

    return fig


def create_parameter_surface_controls():
    """
    Create control elements for the parameter surface visualization.

    Returns:
        A Dash component representing the control panel
    """
    controls = html.Div(
        [
            html.H4(
                "Parameter Surface Controls",
                style={"marginTop": "0", "marginBottom": "15px"},
            ),
            # Metric selection
            html.Div(
                [
                    html.Label("Display Metric:"),
                    dcc.RadioItems(
                        id="surface-metric",
                        options=[
                            {"label": "Relation Probability", "value": "probability"},
                            {"label": "Chi-Square Statistic", "value": "chi2"},
                            {"label": "Shannon Entropy", "value": "entropy"},
                        ],
                        value="probability",
                        labelStyle={"display": "block", "margin": "5px 0"},
                    ),
                ],
                style={"marginBottom": "15px"},
            ),
            # Relation selection for probability view
            html.Div(
                id="relation-selector-container",
                children=[
                    html.Label("Relation to Analyze:"),
                    dcc.Dropdown(
                        id="surface-relation",
                        options=[
                            {"label": f"{rel}: {get_relation_name(rel)}", "value": rel}
                            for rel in ALLEN_RELATION_ORDER
                        ],
                        value="e",  # Default to "equals" relation
                        clearable=False,
                    ),
                ],
                style={"marginBottom": "15px"},
            ),
            # Grid resolution control
            html.Div(
                [
                    html.Label("Grid Resolution:"),
                    dcc.Slider(
                        id="grid-resolution",
                        min=3,
                        max=15,
                        step=1,
                        value=7,
                        marks={3: "3×3", 7: "7×7", 10: "10×10", 15: "15×15"},
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                ],
                style={"marginBottom": "15px"},
            ),
            # Trials per point control
            html.Div(
                [
                    html.Label("Trials per Point:"),
                    dcc.Slider(
                        id="surface-trials",
                        min=200,
                        max=2000,
                        step=200,
                        value=600,
                        marks={200: "200", 600: "600", 1000: "1k", 2000: "2k"},
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                ],
                style={"marginBottom": "15px"},
            ),
            # Generate button
            html.Div(
                [
                    html.Button(
                        "Generate Surface",
                        id="surface-button",
                        style={
                            "backgroundColor": "#3498db",
                            "color": "white",
                            "border": "none",
                            "padding": "10px 20px",
                            "borderRadius": "4px",
                            "fontSize": "16px",
                            "width": "100%",
                            "cursor": "pointer",
                        },
                    )
                ],
                style={"marginTop": "20px"},
            ),
            # Status message area
            html.Div(
                id="surface-status", style={"marginTop": "15px", "minHeight": "60px"}
            ),
        ]
    )

    return controls


def create_parameter_surface_explanation():
    """
    Create an explanation panel for the parameter surface visualization.

    Returns:
        A Dash component with explanation text
    """
    explanation = html.Div(
        [
            html.H4("Understanding the Parameter Surface"),
            html.P(
                [
                    "This 3D visualization shows how the birth probability (pBorn) and death probability (pDie) ",
                    "affect various metrics in Allen relation simulations.",
                ]
            ),
            html.H5("Available Metrics:"),
            html.Ul(
                [
                    html.Li(
                        [
                            html.Strong("Relation Probability: "),
                            "Shows how likely a specific relation is to occur across the parameter space. ",
                            "Higher surfaces indicate parameter combinations that favor that relation.",
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong("Chi-Square Statistic: "),
                            "Measures deviation from the uniform distribution. ",
                            "Higher values (peaks) indicate parameter combinations where the distribution is ",
                            "significantly non-uniform.",
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong("Shannon Entropy: "),
                            "Measures the uncertainty in the distribution. Lower values indicate ",
                            "that fewer relations dominate the distribution.",
                        ]
                    ),
                ]
            ),
            html.H5("Interaction Tips:"),
            html.Ul(
                [
                    html.Li("Click and drag to rotate the 3D view"),
                    html.Li("Scroll to zoom in/out"),
                    html.Li("Double-click to reset the view"),
                    html.Li("Hover over the surface to see exact values"),
                ]
            ),
            html.P(
                [
                    "Try changing the resolution and trials per point to adjust the trade-off ",
                    "between computation time and surface detail.",
                ],
                style={"fontStyle": "italic", "marginTop": "15px"},
            ),
        ],
        style={
            "margin": "20px 0",
            "padding": "15px",
            "backgroundColor": "#f8f8f8",
            "borderRadius": "5px",
        },
    )

    return explanation


if __name__ == "__main__":
    # Test the surface generation with a small grid
    print("Generating parameter surface data (this may take a while)...")

    # Use a small grid for testing
    test_p_values = np.linspace(0.05, 0.4, 5)

    # Generate surface data for the 'equals' relation
    surface_data = generate_parameter_surface_data(
        test_p_values,
        selected_relation="e",
        trials_per_point=300,  # equals relation
        print_results=True,  # Print uniformity test results
    )

    print(
        f"Surface generation complete in {surface_data['computation_time']:.2f} seconds"
    )

    # Create test visualizations
    print("Creating test visualizations...")
    fig_prob = create_3d_surface_plot(surface_data, "probability")
    fig_chi2 = create_3d_surface_plot(surface_data, "chi2")

    # Save HTML visualizations for preview
    import plotly.io as pio

    pio.write_html(fig_prob, file="surface_probability.html", auto_open=True)
    pio.write_html(fig_chi2, file="surface_chi2.html", auto_open=False)
    print("Test visualizations saved as HTML files.")
