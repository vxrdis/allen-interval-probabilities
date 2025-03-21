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

# Import from our modules
from constants import ALLEN_RELATION_ORDER, get_relation_name, RELATION_COLOURS
from simulations import simulateRed, arCode, set_random_seed
from simulations import arSimulate, get_cache_stats
import scipy.stats as stats

# Import shared utilities
from shared_utils import calculate_shannon_entropy, normalize_counts
from analysis_utils import (
    test_uniform_distribution,
    calculate_expected_frequencies,
    analyze_distribution,
)
from visualisation_utils import (
    create_colorscale_for_relation,
    create_control_panel,
    create_explanation_panel,
    generate_3d_surface_figure,
)


def generate_parameter_surface_data(
    p_values,
    selected_relation=None,
    trials_per_point=500,
    use_cache=True,
    verbose=False,  # Add verbose parameter to control output
    progress_callback=None,  # Add callback for progress reporting
):
    """
    Generate simulation data across a grid of birth/death probability parameters.

    Args:
        p_values: List of probability values to use for both pBorn and pDie
        selected_relation: The specific Allen relation to track (default: 'e' for equals)
        trials_per_point: Number of simulation trials for each parameter combination
        use_cache: Whether to use cached simulation results when available
        verbose: Whether to print progress and test results
        progress_callback: Optional callback function taking (completed, total, percentage) for progress tracking

    Returns:
        Dictionary with grid data for 3D surface plotting and computational metadata
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
            if use_cache:
                counts = arSimulate(
                    pBorn, pDie, trials_per_point, test_uniformity=False, use_cache=True
                )
            else:
                # Original method: directly simulate
                # ...existing simulation code...
                pass

            # Calculate total and probabilities
            total_count = sum(counts.values())
            if total_count > 0:
                # ...existing probability calculation...

                # Handle chi-square test
                if total_count >= 13:
                    test_results = test_uniform_distribution(counts)
                    chi2_grid[i, j] = test_results["chi2"]
                    p_value_grid[i, j] = test_results["p_value"]

                    if verbose:
                        print(
                            f"Point ({pBorn:.3f}, {pDie:.3f}): chi²={test_results['chi2']:.4f}, p={test_results['p_value']:.6f} - "
                            + f"{test_results['conclusion']}"
                        )

            # Track progress
            completed_points += 1

            # Report progress through callback or print statement
            if progress_callback:
                progress_callback(
                    completed_points,
                    total_points,
                    completed_points / total_points * 100,
                )
            elif verbose and (
                completed_points % 5 == 0 or completed_points == total_points
            ):
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
        colorscale = create_colorscale_for_relation(selected_relation)
        z_label = "Probability"
        colorbar_title = "Probability"

    elif metric_type == "entropy":
        z_data = surface_data["entropy_grid"]
        title = "Shannon Entropy of Relation Distribution"
        colorscale = "Plasma"  # Consistent color scheme for entropy
        z_label = "Entropy (bits)"
        colorbar_title = "Entropy (bits)"

    else:  # chi-square statistic
        z_data = surface_data["chi2_grid"]
        title = "Chi-Square Statistic (Uniformity Test)"
        colorscale = "Inferno"  # Consistent color scheme for chi-square
        z_label = "Chi² Value"
        colorbar_title = "Chi² Statistic"

    # Create hover template for better interaction
    hover_template = (
        "pBorn: %{x:.3f}<br>"
        + "pDie: %{y:.3f}<br>"
        + f"{z_label}: %{{z:.4f}}<br>"
        + "<extra></extra>"
    )

    # Use the utility function to generate the 3D surface
    fig = generate_3d_surface_figure(
        x_data=pBorn_values,
        y_data=pDie_values,
        z_data=z_data,
        colorscale=colorscale,
        title=title,
        x_title="Birth Probability (pBorn)",
        y_title="Death Probability (pDie)",
        z_title=z_label,
        colorbar_title=colorbar_title,
    )

    # Add custom hover template
    fig.update_traces(hovertemplate=hover_template)

    return fig


def create_parameter_surface_controls():
    """
    Create control elements for the parameter surface visualization.

    Returns:
        A Dash component representing the control panel
    """
    controls = [
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
        # Add missing components that are referenced in callbacks
        html.Div(
            [
                html.Label("Allen Relation:"),
                dcc.Dropdown(
                    id="surface-relation",
                    options=[
                        {"label": f"{rel} ({get_relation_name(rel)})", "value": rel}
                        for rel in ALLEN_RELATION_ORDER
                    ],
                    value="e",  # Default to equals relation
                    clearable=False,
                ),
            ],
            style={"marginBottom": "15px"},
        ),
        html.Div(
            [
                html.Label("Grid Resolution:"),
                dcc.Slider(
                    id="grid-resolution",
                    min=5,
                    max=20,
                    step=1,
                    value=10,
                    marks={i: str(i) for i in range(5, 21, 5)},
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
            ],
            style={"marginBottom": "15px"},
        ),
        html.Div(
            [
                html.Label("Trials per point:"),
                dcc.Input(
                    id="surface-trials",
                    type="number",
                    min=100,
                    max=10000,
                    step=100,
                    value=500,
                    style={"width": "100%"},
                ),
            ],
            style={"marginBottom": "15px"},
        ),
        # Generate button
        html.Button(
            "Generate Surface",
            id="generate-surface",
            style={
                "width": "100%",
                "padding": "10px",
                "backgroundColor": "#3498db",
                "color": "white",
                "border": "none",
                "borderRadius": "5px",
                "cursor": "pointer",
                "marginTop": "10px",
            },
        ),
        # Status indicator
        html.Div(
            id="surface-status",
            children=["Ready to generate."],
            style={"marginTop": "15px"},
        ),
        # Hidden storage component for data
        dcc.Store(id="surface-data"),
    ]

    # Use standardized control panel format
    return create_control_panel("Parameter Surface Controls", controls)


def create_parameter_surface_explanation():
    """
    Create an explanation panel for the parameter surface visualization.

    Returns:
        A Dash component with explanation text
    """
    content = [
        html.P(
            [
                "This 3D visualization shows how the birth probability (pBorn) and death probability (pDie) ",
                "affect various metrics in Allen relation simulations.",
            ]
        ),
        # ...existing content...
    ]

    # Use standardized explanation panel format
    return create_explanation_panel("Understanding the Parameter Surface", content)


if __name__ == "__main__":
    # Test the surface generation with a small grid
    print("Generating parameter surface data (this may take a while)...")

    # Use a small grid for testing
    test_p_values = np.linspace(0.05, 0.4, 5)

    # Generate surface data for the 'equals' relation
    surface_data = generate_parameter_surface_data(
        test_p_values,
        selected_relation="e",
        trials_per_point=300,
        verbose=True,  # Print progress in script mode
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

    # Only save files when running as a script
    pio.write_html(fig_prob, file="surface_probability.html", auto_open=True)
    pio.write_html(fig_chi2, file="surface_chi2.html", auto_open=False)
    print("Test visualizations saved as HTML files.")
