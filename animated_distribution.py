"""
Animated Distribution Evolution for Allen's Interval Algebra

This module provides functions to create and control an animated visualization showing
how the distribution of Allen's interval relations evolves as simulation trials increase.
It includes functions for running simulations in steps, generating frame data, and
creating interactive Plotly visualizations with playback controls.

The visualization shows a bar chart of probabilities for each of Allen's 13 relations,
with a reference line for the uniform distribution and real-time statistical metrics.
"""

import time
import numpy as np
import scipy.stats as stats
from dash import dcc, html
import plotly.graph_objects as go

# Import from our modules
from relations import ALLEN_RELATION_ORDER, get_relation_name
from simulations import simulateRed, arCode, set_random_seed, IntervalSimulator
from constants import ALLEN_RELATION_ORDER, RELATION_COLOURS, get_relation_name
from analysis_utils import (
    test_uniform_distribution,
    calculate_expected_frequencies,
    analyze_distribution,
)

# Import shared utilities
from shared_utils import (
    calculate_shannon_entropy,
    normalize_counts,
    uniform_distribution_value,
)


def run_simulation_in_steps(pBorn, pDie, max_trials, step_size=100):
    """
    Run a simulation in steps, tracking evolution of relation frequencies.

    This implementation uses NumPy arrays for efficient storage and processing of simulation data.

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

    # Initialize counts as NumPy array
    n_relations = len(ALLEN_RELATION_ORDER)
    counts_array = np.zeros(n_relations, dtype=np.int64)

    # Calculate number of frames needed
    n_frames = (max_trials + step_size - 1) // step_size  # Ceiling division

    # Pre-allocate arrays for all frame data
    frame_trials = np.zeros(n_frames, dtype=np.int64)
    frame_counts = np.zeros((n_frames, n_relations), dtype=np.int64)
    frame_probs = np.zeros((n_frames, n_relations), dtype=np.float64)
    frame_chi2 = np.zeros(n_frames, dtype=np.float64)
    frame_pvals = np.zeros(n_frames, dtype=np.float64)
    frame_entropy = np.zeros(n_frames, dtype=np.float64)
    frame_durations = np.zeros(n_frames, dtype=np.float64)
    frame_elapsed = np.zeros(n_frames, dtype=np.float64)

    # For reference, store relation indices in a mapping
    relation_indices = {rel: i for i, rel in enumerate(ALLEN_RELATION_ORDER)}

    # Start timing
    start_time = time.time()

    frame_idx = 0

    # Run simulation in steps
    while total_trials < max_trials:
        step_start_time = time.time()

        # Determine number of trials for this step
        current_step = min(step_size, max_trials - total_trials)

        # Run simulation for this step - FIX: Directly use IntervalSimulator instead of simulateRed
        simulator = IntervalSimulator(pBorn, pDie, current_step)
        step_results = simulator.simulate()

        # Update counts based on relation occurrences in results
        for rel, count in step_results.items():
            counts_array[relation_indices[rel]] += count

        total_trials += current_step

        # Calculate probabilities
        frame_counts[frame_idx] = counts_array.copy()
        total_count = np.sum(counts_array)

        # Debug output to identify if counts are being updated
        print(f"Step {frame_idx+1}: Total count = {total_count}")

        if total_count > 0:
            frame_probs[frame_idx] = counts_array / total_count
        else:
            frame_probs[frame_idx] = 0  # Avoid division by zero

        # Store trial count
        frame_trials[frame_idx] = total_trials

        # Calculate statistical metrics
        if total_count > 0:
            # Convert array back to dict for compatibility with test_uniform_distribution
            counts_dict = {
                rel: counts_array[relation_indices[rel]] for rel in ALLEN_RELATION_ORDER
            }
            test_results = test_uniform_distribution(counts_dict)

            if test_results:  # Add check to ensure test_results is not None
                # Store results in arrays
                frame_chi2[frame_idx] = test_results["chi2"]
                frame_pvals[frame_idx] = test_results["p_value"]

                # Print current step uniformity test results
                print(
                    f"Step {total_trials}: chi²={test_results['chi2']:.4f}, p={test_results['p_value']:.6f} - "
                    + f"{'Reject' if test_results['p_value'] < 0.05 else 'Cannot reject'} uniformity"
                )
            else:
                print(f"Step {total_trials}: Not enough data for uniformity test")
                frame_chi2[frame_idx] = 0
                frame_pvals[frame_idx] = 1.0

            # Calculate entropy from probabilities
            non_zero_probs = frame_probs[frame_idx][frame_probs[frame_idx] > 0]
            frame_entropy[frame_idx] = (
                -np.sum(non_zero_probs * np.log2(non_zero_probs))
                if len(non_zero_probs) > 0
                else 0
            )
        else:
            frame_chi2[frame_idx] = 0
            frame_pvals[frame_idx] = 1.0
            frame_entropy[frame_idx] = 0

        # Record timing information
        step_duration = time.time() - step_start_time
        frame_durations[frame_idx] = step_duration
        frame_elapsed[frame_idx] = time.time() - start_time

        # Move to next frame
        frame_idx += 1

    # Calculate final metrics
    final_counts_dict = {
        rel: counts_array[relation_indices[rel]] for rel in ALLEN_RELATION_ORDER
    }
    final_analysis = analyze_distribution(final_counts_dict)
    final_test_results = final_analysis["uniformity_test"]

    # Handle the case where uniformity test returns None (not enough data)
    if final_test_results is None:
        final_chi2 = 0
        final_p_val = 1.0
        conclusion = "Not enough data for uniformity test"
        print(f"\nFinal results after {total_trials} trials: {conclusion}")
    else:
        final_chi2 = final_test_results["chi2"]
        final_p_val = final_test_results["p_value"]
        conclusion = final_test_results["conclusion"]
        print(f"\nFinal results after {total_trials} trials:")
        print(f"Uniformity test: chi²={final_chi2:.4f}, p={final_p_val:.6f}")
        print(f"{conclusion}")

    # Convert the NumPy array data back to frame dictionaries for compatibility with existing code
    frames = []
    for i in range(frame_idx):
        # Find most/least common relations for this frame
        if np.sum(frame_counts[i]) > 0:
            most_common_idx = np.argmax(frame_probs[i])
            most_common_rel = ALLEN_RELATION_ORDER[most_common_idx]
            most_common_prob = frame_probs[i, most_common_idx]

            least_common_idx = np.argmin(frame_probs[i])
            least_common_rel = ALLEN_RELATION_ORDER[least_common_idx]
            least_common_prob = frame_probs[i, least_common_idx]

            most_common = {
                "label": most_common_rel,
                "count": int(frame_counts[i, most_common_idx]),
                "probability": float(most_common_prob),
            }

            least_common = {
                "label": least_common_rel,
                "count": int(frame_counts[i, least_common_idx]),
                "probability": float(least_common_prob),
            }
        else:
            most_common = {"label": None, "count": 0, "probability": 0}
            least_common = {"label": None, "count": 0, "probability": 0}

        # Build frame dictionary
        frame = {
            "trial_count": int(frame_trials[i]),
            "counts": {
                rel: int(frame_counts[i, relation_indices[rel]])
                for rel in ALLEN_RELATION_ORDER
            },
            "probabilities": {
                rel: float(frame_probs[i, relation_indices[rel]])
                for rel in ALLEN_RELATION_ORDER
            },
            "chi2": float(frame_chi2[i]),
            "p_value": float(frame_pvals[i]),
            "entropy": float(frame_entropy[i]),
            "most_common": most_common,
            "least_common": least_common,
            "step_duration": float(frame_durations[i]),
            "elapsed_time": float(frame_elapsed[i]),
        }
        frames.append(frame)

    # Return results with same structure as before, but internally optimized
    return {
        "params": {"pBorn": pBorn, "pDie": pDie},
        "frames": frames,
        "final_counts": final_counts_dict,
        "final_probabilities": {
            rel: float(frame_probs[-1, relation_indices[rel]])
            for rel in ALLEN_RELATION_ORDER
        },
        "final_analysis": final_analysis,
        "final_test_results": final_test_results,
        "total_duration": time.time() - start_time,
        # Add raw NumPy arrays for direct access if needed
        "_raw": {
            "counts": frame_counts[:frame_idx],
            "probs": frame_probs[:frame_idx],
            "trials": frame_trials[:frame_idx],
            "chi2": frame_chi2[:frame_idx],
            "pvals": frame_pvals[:frame_idx],
            "entropy": frame_entropy[:frame_idx],
            "relation_indices": relation_indices,
        },
    }


def create_distribution_chart(simulation_data, frame_idx=None):
    """
    Create a bar chart showing the distribution of Allen relations.

    Args:
        simulation_data: Data from run_simulation_in_steps
        frame_idx: Index of the frame to display (None for final frame)

    Returns:
        Plotly Figure object with interactive elements
    """
    if (
        not simulation_data
        or "frames" not in simulation_data
        or not simulation_data["frames"]
    ):
        # Return empty figure with instructions if no data
        fig = go.Figure()
        fig.update_layout(
            title="Allen Relation Distribution",
            xaxis_title="Allen Relations",
            yaxis_title="Probability",
            annotations=[
                dict(
                    text="Run a simulation to see the distribution evolution",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=16),
                ),
            ],
        )
        return fig

    # Use final frame if no specific frame is requested
    if frame_idx is None or frame_idx >= len(simulation_data["frames"]):
        frame_idx = len(simulation_data["frames"]) - 1

    frame = simulation_data["frames"][frame_idx]
    pBorn = simulation_data["params"]["pBorn"]
    pDie = simulation_data["params"]["pDie"]
    trial_count = frame["trial_count"]

    # Create figure
    fig = go.Figure()

    # Add bar chart of probabilities with improved hover information
    fig.add_trace(
        go.Bar(
            x=ALLEN_RELATION_ORDER,
            y=[frame["probabilities"][rel] for rel in ALLEN_RELATION_ORDER],
            marker_color=[RELATION_COLOURS[rel] for rel in ALLEN_RELATION_ORDER],
            text=[get_relation_name(rel) for rel in ALLEN_RELATION_ORDER],
            hovertemplate="<b>%{x}: %{text}</b><br>"
            + "Probability: %{y:.4f}<br>"
            + "Count: %{customdata}<extra></extra>",
            customdata=[frame["counts"][rel] for rel in ALLEN_RELATION_ORDER],
        )
    )

    # Add reference line for uniform distribution
    fig.add_trace(
        go.Scatter(
            x=ALLEN_RELATION_ORDER,
            y=[uniform_distribution_value(len(ALLEN_RELATION_ORDER))]
            * len(ALLEN_RELATION_ORDER),
            mode="lines",
            name="Uniform Distribution (1/13)",
            line=dict(color="red", dash="dash"),
            hoverinfo="name",
        )
    )

    # Update layout with enhanced annotations
    fig.update_layout(
        title={
            "text": f"Allen Relation Distribution (pBorn={pBorn}, pDie={pDie})<br>Trials: {trial_count}",
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title="Allen Relations",
        yaxis_title="Probability",
        legend_title="Reference",
        height=500,
        margin=dict(l=50, r=50, t=80, b=50),
        hovermode="closest",
        # Improve chi-square annotation
        annotations=[
            dict(
                x=0.5,
                y=1.08,
                xref="paper",
                yref="paper",
                text=f"Chi² = {frame['chi2']:.3f}, p-value = {frame['p_value']:.6f} "
                + f"({'Reject uniformity' if frame['p_value'] < 0.05 else 'Cannot reject uniformity'})",
                showarrow=False,
                font=dict(size=12),
                bgcolor="rgba(255, 255, 255, 0.7)",
                bordercolor="#333",
                borderwidth=1,
                borderpad=4,
            ),
        ],
    )

    # Add shape to highlight the current most common relation if available
    if "most_common" in frame and frame["most_common"]["label"]:
        most_common_rel = frame["most_common"]["label"]
        most_common_idx = ALLEN_RELATION_ORDER.index(most_common_rel)
        fig.add_shape(
            type="rect",
            x0=most_common_idx - 0.4,
            x1=most_common_idx + 0.4,
            y0=0,
            y1=frame["probabilities"][most_common_rel],
            line=dict(color="gold", width=3),
            fillcolor="rgba(0,0,0,0)",
        )

    # Set y-axis to appropriate range
    max_prob = (
        max([frame["probabilities"][rel] for rel in ALLEN_RELATION_ORDER])
        if frame["probabilities"]
        else 0.2
    )
    fig.update_yaxes(range=[0, max(max_prob * 1.2, 1 / 13 * 1.5)])

    return fig


def create_distribution_animation_controls():
    """
    Create the control elements for the animated distribution.

    Returns:
        A list of Dash components for controlling the animation
    """
    controls = [
        # Info about current animation frame
        html.Div(
            id="animation-info",
            style={
                "textAlign": "center",
                "margin": "0 0 15px 0",
                "padding": "8px",
                "backgroundColor": "#ecf0f1",
                "borderRadius": "4px",
                "fontWeight": "bold",
            },
        ),
        # Playback controls
        html.Div(
            style={
                "display": "flex",
                "alignItems": "center",
                "marginBottom": "15px",
                "justifyContent": "center",
            },
            children=[
                html.Button(
                    "⏪",
                    id="restart-animation",
                    style={
                        "backgroundColor": "#3498db",
                        "color": "white",
                        "border": "none",
                        "padding": "10px 15px",
                        "borderRadius": "4px",
                        "marginRight": "5px",
                    },
                ),
                html.Button(
                    "◀",
                    id="prev-frame",
                    style={
                        "backgroundColor": "#3498db",
                        "color": "white",
                        "border": "none",
                        "padding": "10px 15px",
                        "borderRadius": "4px",
                        "marginRight": "5px",
                    },
                ),
                html.Button(
                    "Play",
                    id="play-button",
                    style={
                        "backgroundColor": "#3498db",
                        "color": "white",
                        "border": "none",
                        "padding": "10px 15px",
                        "borderRadius": "4px",
                        "marginRight": "5px",
                        "minWidth": "60px",
                    },
                ),
                html.Button(
                    "▶",
                    id="next-frame",
                    style={
                        "backgroundColor": "#3498db",
                        "color": "white",
                        "border": "none",
                        "padding": "10px 15px",
                        "borderRadius": "4px",
                        "marginRight": "5px",
                    },
                ),
                html.Button(
                    "⏩",
                    id="end-animation",
                    style={
                        "backgroundColor": "#3498db",
                        "color": "white",
                        "border": "none",
                        "padding": "10px 15px",
                        "borderRadius": "4px",
                    },
                ),
            ],
        ),
        # Animation frame slider
        html.Div(
            style={"marginBottom": "20px", "padding": "0 10px"},
            children=[
                html.Div(
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "marginBottom": "5px",
                    },
                    children=[
                        html.Span("Animation Frame:", style={"fontWeight": "bold"}),
                        html.Span(id="frame-info", children="0/0"),
                    ],
                ),
                dcc.Slider(
                    id="frame-slider",
                    min=0,
                    max=1,
                    step=1,
                    value=0,
                    marks={},
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
                # Animation speed control
                html.Div(
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "marginTop": "10px",
                    },
                    children=[
                        html.Label("Animation Speed:", style={"marginRight": "10px"}),
                        dcc.Slider(
                            id="animation-speed",
                            min=100,
                            max=1000,
                            step=100,
                            value=500,
                            marks={100: "Fast", 500: "Medium", 1000: "Slow"},
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                    ],
                ),
            ],
        ),
        # Hidden interval component for automated animation
        dcc.Interval(id="animation-interval", interval=500, disabled=True),
        # Distribution chart
        dcc.Loading(
            id="loading-distribution",
            type="circle",
            children=[
                dcc.Graph(
                    id="distribution-graph",
                    config={"displayModeBar": True, "scrollZoom": True},
                )
            ],
        ),
        # Explanation panel
        html.Div(
            children=[
                html.H4("About Allen Relation Evolution"),
                html.P(
                    [
                        "This animation shows how the distribution of Allen interval relations evolves ",
                        "as simulation trials increase. The ",
                        html.Span("red dashed line", style={"color": "red"}),
                        " represents the uniform distribution (1/13 ≈ 0.077) for reference.",
                    ]
                ),
                html.P(
                    [
                        "Use the animation controls to explore how the distribution changes over time. ",
                        "The statistics panel shows detailed analysis of the current frame.",
                    ]
                ),
            ],
            style={
                "margin": "15px 0",
                "padding": "15px",
                "backgroundColor": "#f8f8f8",
                "borderRadius": "5px",
            },
        ),
    ]
    return controls


def get_statistical_info(frame_idx, simulation_data):
    """
    Extract statistical information from the simulation data for a specific frame.

    Args:
        frame_idx: Index of the animation frame
        simulation_data: Data from run_simulation_in_steps

    Returns:
        HTML components with statistical analysis
    """
    if (
        not simulation_data
        or "frames" not in simulation_data
        or not simulation_data["frames"]
    ):
        return html.P("No data available. Run a simulation first.")

    # Use final frame if index is out of range
    if frame_idx is None or frame_idx >= len(simulation_data["frames"]):
        frame_idx = len(simulation_data["frames"]) - 1

    frame = simulation_data["frames"][frame_idx]
    trial_count = frame["trial_count"]

    # Extract precomputed metrics if available, or calculate them
    chi2 = frame["chi2"] if "chi2" in frame else 0
    p_value = frame["p_value"] if "p_value" in frame else 1.0
    entropy = frame.get("entropy")
    if entropy is None:  # Calculate entropy if not precomputed
        probs = [frame["probabilities"][rel] for rel in ALLEN_RELATION_ORDER]
        non_zero_probs = [p for p in probs if p > 0]
        entropy = -sum(p * np.log2(p) for p in non_zero_probs) if non_zero_probs else 0

    # Get most and least common relations
    probs = [frame["probabilities"][rel] for rel in ALLEN_RELATION_ORDER]
    most_common_idx = np.argmax(probs)
    most_common_rel = ALLEN_RELATION_ORDER[most_common_idx]
    least_common_idx = np.argmin(probs)
    least_common_rel = ALLEN_RELATION_ORDER[least_common_idx]

    # Create stats panel content with styled sections
    return html.Div(
        [
            html.Div(
                [
                    html.H4(
                        f"Frame Statistics (Trial {trial_count})",
                        style={"margin": "0 0 10px 0", "color": "#3498db"},
                    ),
                    # Uniformity Test Section
                    html.Div(
                        [
                            html.H5("Uniformity Test", style={"margin": "0 0 5px 0"}),
                            html.Table(
                                style={"width": "100%"},
                                children=[
                                    html.Tr(
                                        [
                                            html.Td(
                                                "Chi² statistic:",
                                                style={"paddingRight": "10px"},
                                            ),
                                            html.Td(
                                                f"{chi2:.4f}",
                                                style={"fontWeight": "bold"},
                                            ),
                                        ]
                                    ),
                                    html.Tr(
                                        [
                                            html.Td(
                                                "p-value:",
                                                style={"paddingRight": "10px"},
                                            ),
                                            html.Td(
                                                f"{p_value:.6f}",
                                                style={
                                                    "fontWeight": "bold",
                                                    "color": (
                                                        "red"
                                                        if p_value < 0.05
                                                        else "green"
                                                    ),
                                                },
                                            ),
                                        ]
                                    ),
                                    html.Tr(
                                        [
                                            html.Td(
                                                "Result:",
                                                style={"paddingRight": "10px"},
                                            ),
                                            html.Td(
                                                (
                                                    "Reject uniform distribution"
                                                    if p_value < 0.05
                                                    else "Failed to reject uniform distribution"
                                                ),
                                                style={"fontWeight": "bold"},
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ],
                        style={
                            "marginBottom": "15px",
                            "padding": "10px",
                            "backgroundColor": "#f0f5fa",
                            "borderRadius": "4px",
                        },
                    ),
                    # Distribution Properties Section
                    html.Div(
                        [
                            html.H5(
                                "Distribution Properties", style={"margin": "0 0 5px 0"}
                            ),
                            html.Table(
                                style={"width": "100%"},
                                children=[
                                    html.Tr(
                                        [
                                            html.Td(
                                                "Entropy:",
                                                style={"paddingRight": "10px"},
                                            ),
                                            html.Td(
                                                f"{entropy:.4f} bits",
                                                style={"fontWeight": "bold"},
                                            ),
                                        ]
                                    ),
                                    html.Tr(
                                        [
                                            html.Td(
                                                "Most common:",
                                                style={"paddingRight": "10px"},
                                            ),
                                            html.Td(
                                                f"{most_common_rel} ({get_relation_name(most_common_rel)}): {probs[most_common_idx]:.4f}",
                                                style={"fontWeight": "bold"},
                                            ),
                                        ]
                                    ),
                                    html.Tr(
                                        [
                                            html.Td(
                                                "Least common:",
                                                style={"paddingRight": "10px"},
                                            ),
                                            html.Td(
                                                f"{least_common_rel} ({get_relation_name(least_common_rel)}): {probs[least_common_idx]:.4f}",
                                                style={"fontWeight": "bold"},
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ],
                        style={
                            "padding": "10px",
                            "backgroundColor": "#f0faf5",
                            "borderRadius": "4px",
                        },
                    ),
                ],
                style={
                    "padding": "10px",
                    "backgroundColor": "#f0faf5",
                    "borderRadius": "4px",
                },
            )
        ]
    )


if __name__ == "__main__":
    # Test visualization with a simple simulation
    print("Running test simulation...")
    set_random_seed(42)
    data = run_simulation_in_steps(0.1, 0.1, 1000, 100)

    # Print the final uniformity test results
    chi2, p_val = data["final_uniformity_test"]
    print(f"\nFinal uniformity test results:")
    print(f"chi²={chi2:.4f}, p-value={p_val:.6f}")
    print(
        f"{'Reject' if p_val < 0.05 else 'Cannot reject'} uniform distribution hypothesis"
    )

    print("Creating test visualization...")
    fig = create_distribution_chart(data)
    # If executed as a script, save the figure as HTML for preview
    import plotly.io as pio

    pio.write_html(fig, file="distribution_test.html", auto_open=True)
    print("Test visualization saved as 'distribution_test.html'")
