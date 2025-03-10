"""
Allen's Interval Algebra Interactive Dashboard

This module provides an integrated dashboard for exploring Allen's interval algebra through
multiple interactive visualizations. The dashboard presents three key perspectives:

1. Animated Evolution of Relation Distributions - Shows how the probabilities of Allen's
   13 interval relations evolve as simulation trials increase, with statistical tests
   for uniformity.

2. Interactive Composition Table - Visualizes the composition results between pairs of
   Allen relations through an interactive heatmap, showing either cardinality (number of
   possible outcomes) or entropy (uncertainty).

3. Parameter Space Exploration - Presents a 3D surface plot showing how birth and death
   probabilities affect relation distributions or uniformity test statistics.

The dashboard provides unified controls for simulation parameters and displays statistical
analyses in a dedicated side panel. All visualizations follow Alspaugh's notation for
Allen's 13 relations: p (Before), m (Meets), o (Overlaps), F (Finished-by), D (Contains),
s (Starts), e (Equals), S (Started-by), d (During), f (Finishes), O (Overlapped-by),
M (Met-by), and P (After).

Usage:
    Run this script directly to launch the interactive dashboard:
    python advanced_visualisations.py
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
import time
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

# Import from our modules
from relations import ALLEN_RELATION_ORDER, get_relation_name, compose_relations
from simulations import simulateRed, arCode, set_random_seed

# Define colour scheme for Allen relations (consistent with visualisations.py)
RELATION_COLOURS = {
    "p": "#1f77b4",  # blue
    "m": "#ff7f0e",  # orange
    "o": "#2ca02c",  # green
    "F": "#d62728",  # red
    "D": "#9467bd",  # purple
    "s": "#8c564b",  # brown
    "e": "#e377c2",  # pink
    "S": "#7f7f7f",  # gray
    "d": "#bcbd22",  # olive
    "f": "#17becf",  # cyan
    "O": "#aec7e8",  # light blue
    "M": "#ffbb78",  # light orange
    "P": "#98df8a",  # light green
}


def run_simulation_in_steps(pBorn, pDie, max_trials, step_size=100):
    """
    Run a simulation in steps, tracking evolution of relation frequencies.

    This function simulates Allen relation occurrences and collects data at regular
    intervals to show how the distribution evolves over time.

    Args:
        pBorn: Probability of birth transition
        pDie: Probability of death transition
        max_trials: Maximum number of trials to run
        step_size: Number of trials between data collection points

    Returns:
        Dictionary with simulation data and frames for animation
    """
    # Initialize counters and results storage
    total_trials = 0
    counts = {rel: 0 for rel in ALLEN_RELATION_ORDER}
    frames = []

    # Run simulation in steps
    while total_trials < max_trials:
        # Determine number of trials for this step
        current_step = min(step_size, max_trials - total_trials)

        # Run simulation for this step
        histories = simulateRed(pBorn, pDie, current_step)

        # Update counts based on relation occurrences
        for history in histories:
            relation = arCode(history)
            if relation:
                counts[relation] += 1

        total_trials += current_step

        # Calculate probabilities and statistical metrics
        total_count = sum(counts.values())
        probabilities = {
            rel: counts[rel] / total_count if total_count > 0 else 0
            for rel in ALLEN_RELATION_ORDER
        }

        # Calculate statistical metrics
        expected = [total_count / len(ALLEN_RELATION_ORDER)] * len(ALLEN_RELATION_ORDER)
        observed = [counts[rel] for rel in ALLEN_RELATION_ORDER]

        # Chi-square test (handle case where we don't have enough data)
        if total_count > 0 and all(e > 0 for e in expected):
            chi2, p_val = stats.chisquare(observed, expected)
        else:
            chi2, p_val = 0, 1.0

        # Store frame data
        frames.append(
            {
                "trial_count": total_trials,
                "counts": counts.copy(),
                "probabilities": probabilities,
                "chi2": chi2,
                "p_value": p_val,
            }
        )

    return {
        "params": {"pBorn": pBorn, "pDie": pDie},
        "frames": frames,
        "final_counts": counts,
        "final_probabilities": probabilities,
    }


def create_animated_distribution_chart(simulation_data, frame_idx=None):
    """
    Create an animated bar chart showing evolution of relation probabilities.

    Args:
        simulation_data: Data from run_simulation_in_steps
        frame_idx: Index of the frame to display (None for final frame)

    Returns:
        Plotly Figure object
    """
    if (
        not simulation_data
        or "frames" not in simulation_data
        or not simulation_data["frames"]
    ):
        # Return empty figure if no data
        return go.Figure()

    # Use final frame if no specific frame is requested
    if frame_idx is None or frame_idx >= len(simulation_data["frames"]):
        frame_idx = len(simulation_data["frames"]) - 1

    frame = simulation_data["frames"][frame_idx]
    pBorn = simulation_data["params"]["pBorn"]
    pDie = simulation_data["params"]["pDie"]
    trial_count = frame["trial_count"]

    # Create figure
    fig = go.Figure()

    # Add bar chart of probabilities
    fig.add_trace(
        go.Bar(
            x=ALLEN_RELATION_ORDER,
            y=[frame["probabilities"][rel] for rel in ALLEN_RELATION_ORDER],
            marker_color=[RELATION_COLOURS[rel] for rel in ALLEN_RELATION_ORDER],
            text=[get_relation_name(rel) for rel in ALLEN_RELATION_ORDER],
            hovertemplate="%{x}: %{y:.4f}<br>%{text}<extra></extra>",
        )
    )

    # Add reference line for uniform distribution
    fig.add_trace(
        go.Scatter(
            x=ALLEN_RELATION_ORDER,
            y=[1 / 13] * len(ALLEN_RELATION_ORDER),
            mode="lines",
            name="Uniform Distribution (1/13)",
            line=dict(color="red", dash="dash"),
        )
    )

    # Update layout
    fig.update_layout(
        title=f"Allen Relation Distribution Evolution (pBorn={pBorn}, pDie={pDie}, Trials: {trial_count})",
        xaxis_title="Allen Relations",
        yaxis_title="Probability",
        legend_title="Reference",
        height=500,
        margin=dict(l=50, r=50, t=80, b=80),
        # Annotation for chi-square statistics
        annotations=[
            dict(
                x=0.5,
                y=1.05,
                xref="paper",
                yref="paper",
                text=f"Chi² = {frame['chi2']:.3f}, p-value = {frame['p_value']:.6f} "
                + f"({'Reject' if frame['p_value'] < 0.05 else 'Accept'} uniform distribution hypothesis)",
                showarrow=False,
                font=dict(size=12),
            )
        ],
    )

    return fig


def create_composition_matrix():
    """
    Create a theoretical composition matrix based on Allen's interval algebra.

    This function computes the theoretical composition results for all pairs of
    Allen relations, following Alspaugh's notation and ordering.

    Returns:
        Dictionary containing:
        - compositions: The raw composition results for each relation pair
        - cardinality: A numpy array with counts of possible outcomes
        - entropy: A numpy array with Shannon entropy values
    """
    n = len(ALLEN_RELATION_ORDER)
    compositions = {}  # To store the actual composition results
    cardinality_matrix = np.zeros((n, n))
    entropy_matrix = np.zeros((n, n))

    # Compute compositions for all relation pairs
    for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
        for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
            # Get the theoretical composition result
            result = compose_relations(rel1, rel2)

            # Store the raw composition result
            compositions[(rel1, rel2)] = result

            # Calculate cardinality (number of possible relations in result)
            cardinality_matrix[i, j] = len(result)

            # Calculate entropy (assuming uniform distribution over possible results)
            if len(result) > 0:
                # Uniform distribution over possible outcomes
                p = 1.0 / len(result)
                entropy_matrix[i, j] = -len(result) * p * np.log2(p)

    return {
        "compositions": compositions,
        "cardinality": cardinality_matrix,
        "entropy": entropy_matrix,
    }


def generate_interactive_composition_heatmap(comp_data, view_mode="cardinality"):
    """
    Generate an interactive heatmap visualization of the composition table.

    This function creates a Plotly figure showing either the cardinality (number of
    possible outcomes) or the Shannon entropy of each composition result.

    Args:
        comp_data: Dictionary containing composition data from create_composition_matrix()
        view_mode: Either "cardinality" or "entropy" to select the display mode

    Returns:
        Plotly Figure object with the interactive heatmap
    """
    # Select the appropriate data based on view mode
    if view_mode == "entropy":
        z_data = comp_data["entropy"]
        colorscale = "Viridis"  # Green-blue scale for entropy
        title = "Allen Relation Composition Table - Entropy"
        colorbar_title = "Shannon Entropy (bits)"
        hover_format = ".3f bits"
    else:  # cardinality view
        z_data = comp_data["cardinality"]
        colorscale = "Blues"  # Blue scale for counts
        title = "Allen Relation Composition Table - Number of Possible Relations"
        colorbar_title = "Count"
        hover_format = ".0f relations"

    # Create the heatmap trace
    heatmap = go.Heatmap(
        z=z_data,
        x=ALLEN_RELATION_ORDER,
        y=ALLEN_RELATION_ORDER,
        colorscale=colorscale,
        showscale=True,
        colorbar=dict(
            title=colorbar_title,
            titleside="right",
        ),
        hovertemplate="Composition: %{y} ∘ %{x}<br>"
        + f"Value: %{{z:{hover_format}}}<extra></extra>",
    )

    # Create the figure
    fig = go.Figure(data=heatmap)

    # Add hover annotations with detailed composition information
    for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
        for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
            # Get the composition result
            result = comp_data["compositions"].get((rel1, rel2), [])

            # Format result for display
            if result:
                result_str = ", ".join(result)
                count = len(result)
                entropy = -count * (1 / count) * np.log2(1 / count) if count > 0 else 0

                # Add invisible scatter point with custom hover text
                fig.add_trace(
                    go.Scatter(
                        x=[j],
                        y=[i],
                        mode="markers",
                        marker=dict(size=1, color="rgba(0,0,0,0)"),
                        hoverinfo="text",
                        hovertext=(
                            f"<b>{rel1} ∘ {rel2}</b><br>"
                            + f"Possible relations: {result_str}<br>"
                            + f"Count: {count}<br>"
                            + f"Entropy: {entropy:.3f} bits"
                        ),
                        showlegend=False,
                    )
                )

    # Update layout
    fig.update_layout(
        title=title,
        xaxis=dict(title="Second Relation (rel₂)", side="top"),
        yaxis=dict(
            title="First Relation (rel₁)",
            autorange="reversed",  # To match conventional matrix orientation
        ),
        height=700,
        width=800,
        margin=dict(t=100, b=50, l=100, r=50),
    )

    return fig


def generate_parameter_surface_data(p_values, selected_relation, trials_per_point=500):
    """
    Generate simulation data across a grid of birth/death probability parameters.

    This function runs simulations for multiple combinations of pBorn and pDie,
    collecting both the probability of a selected relation and the chi-square
    statistic at each point.

    Args:
        p_values: List of probability values to use for both pBorn and pDie
        selected_relation: The specific Allen relation to track
        trials_per_point: Number of simulation trials for each parameter combination

    Returns:
        Dictionary with grid data for 3D surface plotting
    """
    grid_size = len(p_values)
    # Initialize arrays for storing results
    probability_grid = np.zeros((grid_size, grid_size))
    chi2_grid = np.zeros((grid_size, grid_size))
    p_value_grid = np.zeros((grid_size, grid_size))

    # Run simulations for all parameter combinations
    for i, pBorn in enumerate(p_values):
        for j, pDie in enumerate(p_values):
            # Set a fixed random seed for reproducibility
            set_random_seed()

            # Run a smaller simulation for each grid point (single step)
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
                # Track probability of the selected relation
                probability_grid[i, j] = counts.get(selected_relation, 0) / total_count

                # Calculate chi-square statistic for uniformity test
                observed = [counts[rel] for rel in ALLEN_RELATION_ORDER]
                expected = [total_count / len(ALLEN_RELATION_ORDER)] * len(
                    ALLEN_RELATION_ORDER
                )

                # Handle case where not enough data for chi-square test
                if total_count >= 13:  # At least one expected sample per category
                    chi2, p_val = stats.chisquare(observed, expected)
                    chi2_grid[i, j] = chi2
                    p_value_grid[i, j] = p_val

    return {
        "pBorn_values": p_values,
        "pDie_values": p_values,
        "probability_grid": probability_grid,
        "chi2_grid": chi2_grid,
        "p_value_grid": p_value_grid,
        "selected_relation": selected_relation,
    }


def create_3d_surface_plot(surface_data, metric_type="probability"):
    """
    Create a 3D surface plot visualizing parameter effects on Allen relations.

    Args:
        surface_data: Output from generate_parameter_surface_data
        metric_type: Type of data to visualize - "probability" or "chi2"

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
        color_scale = "Viridis"
        z_label = "Probability"
        colorbar_title = "Probability"
    else:  # chi-square statistic
        z_data = surface_data["chi2_grid"]
        title = "Chi-Square Statistic (Uniformity Test)"
        color_scale = "Inferno"
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


# Define style constants for consistent look and feel
COLORS = {
    "background": "#f8f9fa",
    "text": "#2c3e50",
    "primary": "#3498db",
    "secondary": "#e74c3c",
    "light": "#ecf0f1",
    "dark": "#34495e",
    "success": "#2ecc71",
    "warning": "#f39c12",
}

STYLES = {
    "card": {
        "padding": "15px",
        "borderRadius": "8px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
        "backgroundColor": "white",
        "marginBottom": "15px",
    },
    "header": {
        "color": COLORS["text"],
        "padding": "10px",
        "marginBottom": "15px",
        "borderBottom": f'1px solid {COLORS["light"]}',
    },
    "control_panel": {
        "padding": "15px",
        "backgroundColor": COLORS["light"],
        "borderRadius": "8px",
        "marginBottom": "15px",
    },
    "visualization_container": {
        "backgroundColor": "white",
        "padding": "15px",
        "borderRadius": "8px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
        "marginBottom": "15px",
    },
    "button": {
        "backgroundColor": COLORS["primary"],
        "color": "white",
        "border": "none",
        "padding": "10px 15px",
        "borderRadius": "4px",
        "cursor": "pointer",
    },
    "stats_panel": {
        "padding": "15px",
        "backgroundColor": COLORS["light"],
        "borderRadius": "8px",
        "marginBottom": "15px",
    },
}

# Setup the Dash app
app = dash.Dash(
    __name__,
    title="Allen's Interval Algebra Explorer",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

# Define the layout of the dashboard
app.layout = html.Div(
    style={
        "backgroundColor": COLORS["background"],
        "minHeight": "100vh",
        "padding": "20px",
    },
    children=[
        # Header
        html.Div(
            style=STYLES["header"],
            children=[
                html.H1(
                    "Allen's Interval Algebra Interactive Explorer",
                    style={"textAlign": "center"},
                ),
                html.P(
                    """
                    Explore the empirical probabilities, compositions, and parameter effects in Allen's interval algebra.
                    Use the controls in the side panel to adjust simulation parameters and analyze the results.
                    """,
                    style={
                        "textAlign": "center",
                        "maxWidth": "800px",
                        "margin": "0 auto",
                    },
                ),
            ],
        ),
        # Main content area with sidebar and visualization pane
        html.Div(
            style={"display": "flex", "flexDirection": "row", "gap": "20px"},
            children=[
                # Side panel with controls and stats
                html.Div(
                    style={"flex": "1", "maxWidth": "300px"},
                    children=[
                        # Simulation Controls
                        html.Div(
                            style=STYLES["card"],
                            children=[
                                html.H3("Simulation Controls", style={"marginTop": 0}),
                                # Birth probability slider
                                html.Div(
                                    style={"marginBottom": "15px"},
                                    children=[
                                        html.Label("Birth Probability (pBorn):"),
                                        dcc.Slider(
                                            id="pborn-slider",
                                            min=0.01,
                                            max=0.5,
                                            step=0.01,
                                            value=0.1,
                                            marks={
                                                0.01: "0.01",
                                                0.1: "0.1",
                                                0.25: "0.25",
                                                0.5: "0.5",
                                            },
                                            tooltip={
                                                "placement": "bottom",
                                                "always_visible": True,
                                            },
                                        ),
                                    ],
                                ),
                                # Death probability slider
                                html.Div(
                                    style={"marginBottom": "15px"},
                                    children=[
                                        html.Label("Death Probability (pDie):"),
                                        dcc.Slider(
                                            id="pdie-slider",
                                            min=0.01,
                                            max=0.5,
                                            step=0.01,
                                            value=0.1,
                                            marks={
                                                0.01: "0.01",
                                                0.1: "0.1",
                                                0.25: "0.25",
                                                0.5: "0.5",
                                            },
                                            tooltip={
                                                "placement": "bottom",
                                                "always_visible": True,
                                            },
                                        ),
                                    ],
                                ),
                                # Number of trials slider
                                html.Div(
                                    style={"marginBottom": "15px"},
                                    children=[
                                        html.Label("Number of Trials:"),
                                        dcc.Slider(
                                            id="trials-slider",
                                            min=100,
                                            max=10000,
                                            step=100,
                                            value=1000,
                                            marks={
                                                100: "100",
                                                1000: "1k",
                                                5000: "5k",
                                                10000: "10k",
                                            },
                                            tooltip={
                                                "placement": "bottom",
                                                "always_visible": True,
                                            },
                                        ),
                                    ],
                                ),
                                # Step size for animation
                                html.Div(
                                    style={"marginBottom": "20px"},
                                    children=[
                                        html.Label("Animation Step Size:"),
                                        dcc.Slider(
                                            id="step-slider",
                                            min=10,
                                            max=500,
                                            step=10,
                                            value=100,
                                            marks={
                                                10: "10",
                                                100: "100",
                                                250: "250",
                                                500: "500",
                                            },
                                            tooltip={
                                                "placement": "bottom",
                                                "always_visible": True,
                                            },
                                        ),
                                    ],
                                ),
                                # Run button
                                html.Button(
                                    "Run Simulation",
                                    id="run-button",
                                    style=STYLES["button"],
                                ),
                                # Status message area
                                html.Div(
                                    id="simulation-status", style={"marginTop": "10px"}
                                ),
                            ],
                        ),
                        # Statistics Panel
                        html.Div(
                            style=STYLES["card"],
                            children=[
                                html.H3("Statistical Analysis", style={"marginTop": 0}),
                                html.Div(
                                    id="stats-panel",
                                    children=[
                                        html.P(
                                            "Run a simulation to see statistical results."
                                        )
                                    ],
                                ),
                            ],
                        ),
                        # Visualization-specific controls
                        html.Div(
                            style=STYLES["card"],
                            children=[
                                html.H3(
                                    "Visualization Options", style={"marginTop": 0}
                                ),
                                # Composition view mode
                                html.Div(
                                    id="composition-controls",
                                    style={"marginBottom": "15px"},
                                    children=[
                                        html.Label("Composition Table View:"),
                                        dcc.RadioItems(
                                            id="heatmap-view-mode",
                                            options=[
                                                {
                                                    "label": "Cardinality",
                                                    "value": "cardinality",
                                                },
                                                {
                                                    "label": "Entropy",
                                                    "value": "entropy",
                                                },
                                            ],
                                            value="cardinality",
                                            labelStyle={"marginRight": "10px"},
                                        ),
                                    ],
                                ),
                                # 3D Surface options
                                html.Div(
                                    id="surface-controls",
                                    children=[
                                        html.Label("Parameter Surface Metric:"),
                                        dcc.RadioItems(
                                            id="surface-metric",
                                            options=[
                                                {
                                                    "label": "Relation Probability",
                                                    "value": "probability",
                                                },
                                                {
                                                    "label": "Chi-Square Statistic",
                                                    "value": "chi2",
                                                },
                                            ],
                                            value="probability",
                                            labelStyle={"marginRight": "10px"},
                                        ),
                                        html.Div(
                                            style={"marginTop": "10px"},
                                            children=[
                                                html.Label("Relation to Analyze:"),
                                                dcc.Dropdown(
                                                    id="surface-relation",
                                                    options=[
                                                        {
                                                            "label": f"{rel}: {get_relation_name(rel)}",
                                                            "value": rel,
                                                        }
                                                        for rel in ALLEN_RELATION_ORDER
                                                    ],
                                                    value="e",  # Default to "equals" relation
                                                    clearable=False,
                                                ),
                                            ],
                                        ),
                                        html.Button(
                                            "Generate Surface",
                                            id="surface-button",
                                            style={
                                                **STYLES["button"],
                                                "marginTop": "10px",
                                            },
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                # Main visualization area with tabs
                html.Div(
                    style={"flex": "3"},
                    children=[
                        dcc.Tabs(
                            id="visualization-tabs",
                            value="distribution-tab",
                            children=[
                                # Distribution Evolution Tab
                                dcc.Tab(
                                    label="Distribution Evolution",
                                    value="distribution-tab",
                                    children=[
                                        html.Div(
                                            style=STYLES["visualization_container"],
                                            children=[
                                                # Animation controls
                                                html.Div(
                                                    style={
                                                        "display": "flex",
                                                        "alignItems": "center",
                                                        "marginBottom": "15px",
                                                        "justifyContent": "center",
                                                    },
                                                    children=[
                                                        html.Button(
                                                            "◀",
                                                            id="prev-frame",
                                                            style={
                                                                **STYLES["button"],
                                                                "marginRight": "5px",
                                                            },
                                                        ),
                                                        html.Button(
                                                            "Play",
                                                            id="play-button",
                                                            style={
                                                                **STYLES["button"],
                                                                "marginRight": "5px",
                                                            },
                                                        ),
                                                        html.Button(
                                                            "▶",
                                                            id="next-frame",
                                                            style=STYLES["button"],
                                                        ),
                                                    ],
                                                ),
                                                # Animation frame slider
                                                html.Div(
                                                    style={"marginBottom": "20px"},
                                                    children=[
                                                        html.Label("Animation Frame:"),
                                                        dcc.Slider(
                                                            id="frame-slider",
                                                            min=0,
                                                            max=1,
                                                            step=1,
                                                            value=0,
                                                            marks={},
                                                        ),
                                                    ],
                                                ),
                                                # Animation interval component (hidden)
                                                dcc.Interval(
                                                    id="animation-interval",
                                                    interval=500,
                                                    disabled=True,
                                                ),
                                                # Distribution plot
                                                dcc.Loading(
                                                    id="loading-distribution",
                                                    type="circle",
                                                    children=[
                                                        dcc.Graph(
                                                            id="distribution-graph"
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                # Composition Table Tab
                                dcc.Tab(
                                    label="Composition Table",
                                    value="composition-tab",
                                    children=[
                                        html.Div(
                                            style=STYLES["visualization_container"],
                                            children=[
                                                html.P(
                                                    """
                                                    This heatmap shows the result of composing Allen relations. When
                                                    interval x has relation r₁ to interval y, and y has relation r₂ to z,
                                                    the composition tells us what relation(s) could hold between x and z.
                                                    Use the controls in the side panel to switch between views.
                                                    """
                                                ),
                                                # Composition heatmap
                                                dcc.Loading(
                                                    id="loading-composition",
                                                    type="circle",
                                                    children=[
                                                        dcc.Graph(
                                                            id="composition-heatmap"
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                # Parameter Surface Tab
                                dcc.Tab(
                                    label="Parameter Surface",
                                    value="surface-tab",
                                    children=[
                                        html.Div(
                                            style=STYLES["visualization_container"],
                                            children=[
                                                html.P(
                                                    """
                                                    This 3D surface visualization shows how birth probability (pBorn)
                                                    and death probability (pDie) affect Allen relations or statistical measures.
                                                    Click and drag to rotate the view.
                                                    Use the controls in the side panel to adjust what is displayed.
                                                    """
                                                ),
                                                # Surface plot
                                                dcc.Loading(
                                                    id="loading-surface",
                                                    type="circle",
                                                    children=[
                                                        dcc.Graph(
                                                            id="parameter-surface"
                                                        )
                                                    ],
                                                ),
                                                # Surface generation status
                                                html.Div(id="surface-status"),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
            ],
        ),
        # Hidden storage components for data
        dcc.Store(id="simulation-data"),  # For simulation results
        dcc.Store(id="composition-data"),  # For composition matrix data
        dcc.Store(id="surface-data"),  # For parameter surface data
    ],
)


# Define callbacks
@app.callback(
    [
        Output("simulation-data", "data"),
        Output("simulation-status", "children"),
        Output("frame-slider", "max"),
        Output("frame-slider", "marks"),
        Output("frame-slider", "value"),
    ],
    Input("run-button", "n_clicks"),
    [
        State("pborn-slider", "value"),
        State("pdie-slider", "value"),
        State("trials-slider", "value"),
        State("step-slider", "value"),
    ],
    prevent_initial_call=True,
)
def run_simulation(n_clicks, pborn, pdie, trials, step_size):
    """Callback to run simulation when button is clicked"""
    if n_clicks > 0:
        # Set random seed for reproducibility
        set_random_seed()

        # Run simulation
        simulation_data = run_simulation_in_steps(pborn, pdie, trials, step_size)

        # Create marks for slider
        num_frames = len(simulation_data["frames"])
        step = max(1, num_frames // 10)
        marks = {
            i: f"{simulation_data['frames'][i]['trial_count']}"
            for i in range(0, num_frames, step)
        }

        if num_frames - 1 not in marks:
            marks[num_frames - 1] = (
                f"{simulation_data['frames'][num_frames - 1]['trial_count']}"
            )

        return (
            simulation_data,
            f"Simulation completed: {trials} trials with pBorn={pborn}, pDie={pdie}",
            num_frames - 1,
            marks,
            0,
        )

    return {}, "Click 'Run Simulation' to start", 1, {}, 0


@app.callback(
    Output("distribution-graph", "figure"),
    Input("frame-slider", "value"),
    State("simulation-data", "data"),
    prevent_initial_call=True,
)
def update_animation(frame_idx, simulation_data):
    """Update animation based on selected frame"""
    return create_animated_distribution_chart(simulation_data, frame_idx)


@app.callback(
    Output("stats-panel", "children"),
    Input("frame-slider", "value"),
    State("simulation-data", "data"),
    prevent_initial_call=True,
)
def update_stats(frame_idx, simulation_data):
    """Update statistical analysis based on selected frame"""
    if (
        not simulation_data
        or "frames" not in simulation_data
        or not simulation_data["frames"]
    ):
        return "No data available. Run a simulation first."

    # Use final frame if index is out of range
    if frame_idx is None or frame_idx >= len(simulation_data["frames"]):
        frame_idx = len(simulation_data["frames"]) - 1

    frame = simulation_data["frames"][frame_idx]
    trial_count = frame["trial_count"]
    chi2 = frame["chi2"]
    p_value = frame["p_value"]

    # Calculate entropy of the distribution
    probs = [frame["probabilities"][rel] for rel in ALLEN_RELATION_ORDER]
    probs_filtered = [p for p in probs if p > 0]
    entropy = -sum(p * np.log2(p) for p in probs_filtered) if probs_filtered else 0

    # Create stats panel content
    return html.Div(
        [
            html.P(
                f"Current frame: {frame_idx + 1} of {len(simulation_data['frames'])}"
            ),
            html.P(f"Trials: {trial_count}"),
            html.Hr(),
            html.P(
                [
                    html.Strong("Chi-square Test for Uniform Distribution:"),
                    html.Br(),
                    f"Chi² statistic: {chi2:.4f}",
                    html.Br(),
                    f"p-value: {p_value:.8f}",
                    html.Br(),
                    html.Strong(
                        "Reject null hypothesis (distribution is not uniform)"
                        if p_value < 0.05
                        else "Fail to reject null hypothesis (distribution may be uniform)"
                    ),
                ]
            ),
            html.Hr(),
            html.P(
                [
                    html.Strong("Distribution Properties:"),
                    html.Br(),
                    f"Entropy: {entropy:.4f} bits",
                    html.Br(),
                    f"Maximum probability: {max(probs):.4f} ({ALLEN_RELATION_ORDER[np.argmax(probs)]})",
                    html.Br(),
                    f"Minimum probability: {min(probs):.4f} ({ALLEN_RELATION_ORDER[np.argmin(probs)]})",
                ]
            ),
        ]
    )


@app.callback(
    [
        Output("animation-interval", "disabled"),
        Output("frame-slider", "value"),
        Output("play-button", "children"),
    ],
    [
        Input("play-button", "n_clicks"),
        Input("next-frame", "n_clicks"),
        Input("prev-frame", "n_clicks"),
        Input("animation-interval", "n_intervals"),
    ],
    [
        State("frame-slider", "value"),
        State("frame-slider", "max"),
        State("animation-interval", "disabled"),
        State("play-button", "children"),
    ],
    prevent_initial_call=True,
)
def control_animation(
    play_clicks,
    next_clicks,
    prev_clicks,
    n_intervals,
    current_frame,
    max_frame,
    is_disabled,
    play_label,
):
    """Control the animation playback"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_disabled, current_frame, play_label

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "play-button":
        # Toggle play state
        new_disabled = not is_disabled
        new_label = "Pause" if new_disabled == False else "Play"
        return new_disabled, current_frame, new_label

    elif trigger_id == "next-frame":
        # Go to next frame
        next_frame = min(current_frame + 1, max_frame)
        return is_disabled, next_frame, play_label

    elif trigger_id == "prev-frame":
        # Go to previous frame
        prev_frame = max(current_frame - 0, 0)
        return is_disabled, prev_frame, play_label

    elif trigger_id == "animation-interval" and not is_disabled:
        # Auto-advance frame for animation
        next_frame = current_frame + 1
        # Loop back to beginning if we reach the end
        if next_frame > max_frame:
            next_frame = 0
        return is_disabled, next_frame, play_label

    # Default: no change
    return is_disabled, current_frame, play_label


# Add callback to compute composition data and update heatmap
@app.callback(
    [Output("composition-data", "data"), Output("composition-heatmap", "figure")],
    [Input("heatmap-view-mode", "value")],
    State("composition-data", "data"),
    prevent_initial_call=False,
)
def update_composition_heatmap(view_mode, existing_data):
    """
    Update the composition heatmap based on the selected view mode.

    Args:
        view_mode: Either "cardinality" or "entropy"
        existing_data: Previously computed composition data, if any

    Returns:
        Updated composition data and Plotly figure
    """
    # Check if we already have composition data
    if not existing_data:
        # Compute composition data if it doesn't exist
        comp_data = create_composition_matrix()
    else:
        comp_data = existing_data

    # Generate the heatmap
    fig = generate_interactive_composition_heatmap(comp_data, view_mode)

    return comp_data, fig


# Add callback for the parameter surface
@app.callback(
    [
        Output("surface-data", "data"),
        Output("parameter-surface", "figure"),
        Output("surface-status", "children"),
    ],
    Input("surface-button", "n_clicks"),
    [
        State("surface-metric", "value"),
        State("surface-relation", "value"),
        State("grid-resolution", "value"),
        State("surface-trials", "value"),
    ],
    prevent_initial_call=True,
)
def update_parameter_surface(n_clicks, metric, relation, resolution, trials_per_point):
    """
    Generate and update the parameter surface plot based on user selections.

    Args:
        n_clicks: Number of times the generate button has been clicked
        metric: Type of data to visualize ("probability" or "chi2")
        relation: The Allen relation to track for probability visualization
        resolution: Number of points along each axis (grid size)
        trials_per_point: Number of simulation trials per grid point

    Returns:
        Tuple of (surface data, figure, status message)
    """
    if n_clicks == 0:
        # Return empty figure on initial load
        return None, go.Figure(), ""

    # Generate p_values based on resolution (from 0.01 to 0.5)
    p_values = np.linspace(0.01, 0.5, resolution)

    # Generate surface data through simulation
    start_time = time.time()
    surface_data = generate_parameter_surface_data(p_values, relation, trials_per_point)
    elapsed_time = time.time() - start_time

    # Create the 3D surface plot
    fig = create_3d_surface_plot(surface_data, metric)

    # Create status message
    status = html.Div(
        [
            html.P(f"Surface generated in {elapsed_time:.2f} seconds"),
            html.P(
                f"Grid size: {resolution}x{resolution}, {trials_per_point} trials per point"
            ),
        ]
    )

    return surface_data, fig, status


# Define a new callback to render initial composition heatmap on page load
@app.callback(
    [Output("composition-data", "data"), Output("composition-heatmap", "figure")],
    [Input("heatmap-view-mode", "value")],
    prevent_initial_call=False,
)
def initialize_composition_heatmap(view_mode):
    """Initialize the composition heatmap when the app first loads"""
    # Compute composition data
    comp_data = create_composition_matrix()

    # Generate the heatmap
    fig = generate_interactive_composition_heatmap(comp_data, view_mode)

    return comp_data, fig


# Add placeholder for empty parameter surface
@app.callback(
    Output("parameter-surface", "figure"), Input("visualization-tabs", "value")
)
def initialize_surface_plot(tab_value):
    """Initialize an empty 3D surface plot as a placeholder"""
    if tab_value != "surface-tab":
        return dash.no_update

    # Create an empty figure with instructions
    fig = go.Figure()

    fig.update_layout(
        title="Parameter Surface Plot",
        scene=dict(
            xaxis_title="Birth Probability (pBorn)",
            yaxis_title="Death Probability (pDie)",
            zaxis_title="Value",
        ),
        annotations=[
            dict(
                showarrow=False,
                x=0.5,
                y=0.5,
                text="Click 'Generate Surface' to create a visualization",
                xref="paper",
                yref="paper",
            )
        ],
    )

    return fig


# Run the application
if __name__ == "__main__":
    print("Starting Allen's Interval Algebra Explorer Dashboard...")
    print("Open a web browser and navigate to http://127.0.0.1:8050/")
    app.run_server(debug=True)
