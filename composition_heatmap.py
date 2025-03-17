"""
Interactive Composition Heatmap for Allen's Interval Algebra

This module provides functions to create and interact with a heatmap visualization
of Allen's interval relation compositions. The heatmap can be toggled between two views:
1. Cardinality View - Shows the number of possible relations for each composition
2. Entropy View - Shows the Shannon entropy (uncertainty) of each composition result

Each cell in the heatmap represents the composition of two Allen relations, with
detailed tooltips showing the specific relations that can result from the composition.

The visualization helps understand the theoretical constraints in Allen's interval
algebra and identify compositions that yield more specific (fewer possible outcomes)
or more ambiguous (higher entropy) results.
"""

import numpy as np
import pandas as pd
from dash import dcc, html
import plotly.graph_objects as go

# Import from our modules
from relations import compose_relations
from constants import ALLEN_RELATION_ORDER, get_relation_name

# Import shared utilities
from shared_utils import calculate_shannon_entropy


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

            # Calculate entropy using shared utility function
            if len(result) > 0:
                # Uniform distribution over possible outcomes
                uniform_p = 1.0 / len(result)
                probs = [uniform_p] * len(result)
                entropy_matrix[i, j] = calculate_shannon_entropy(probs)

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
            title=dict(text=colorbar_title),
        ),
        hovertemplate="Composition: %{y} ∘ %{x}<br>"
        + f"Value: %{{z:{hover_format}}}<extra></extra>",
    )

    # Create the figure
    fig = go.Figure(data=heatmap)

    # Add hover annotations with detailed composition information
    for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
        for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
            # Get the composition result - handle string key format
            key = f"{rel1},{rel2}"
            result = comp_data["compositions"].get(key, [])

            # Format result for display
            if result:
                result_str = ", ".join(result)
                count = len(result)

                # Use shared utility function for entropy calculation
                uniform_probs = [1 / count] * count if count > 0 else []
                entropy = calculate_shannon_entropy(uniform_probs)

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


def create_composition_controls():
    """
    Create control elements for the composition heatmap.

    Returns:
        A Dash component representing the control panel
    """
    controls = html.Div(
        [
            html.H4(
                "Composition Table Controls",
                style={"marginTop": "0", "marginBottom": "15px"},
            ),
            html.Label("View Mode:"),
            dcc.RadioItems(
                id="heatmap-view-mode",
                options=[
                    {"label": "Cardinality (count)", "value": "cardinality"},
                    {"label": "Entropy (uncertainty)", "value": "entropy"},
                ],
                value="cardinality",
                labelStyle={"display": "inline-block", "marginRight": "15px"},
            ),
            html.Div(
                [
                    html.P(
                        [
                            html.Strong("Cardinality View: "),
                            "Shows the number of possible relations that could result from each composition. ",
                            "Fewer possible outcomes (darker blue) means more specific, constrained results.",
                        ],
                        style={"fontSize": "13px", "marginTop": "15px"},
                    ),
                    html.P(
                        [
                            html.Strong("Entropy View: "),
                            "Shows the information-theoretic uncertainty (Shannon entropy) in each composition result. ",
                            "Lower entropy (blue/green) means more certainty in the outcome.",
                        ],
                        style={"fontSize": "13px"},
                    ),
                    html.P(
                        "Hover over cells to see the full list of possible relations for each composition.",
                        style={
                            "fontSize": "13px",
                            "fontStyle": "italic",
                            "marginTop": "15px",
                        },
                    ),
                ],
                style={
                    "backgroundColor": "#f8f8f8",
                    "padding": "10px",
                    "borderRadius": "4px",
                    "marginTop": "10px",
                },
            ),
        ]
    )
    return controls


def create_composition_explanation():
    """
    Create an explanation panel for the composition heatmap.

    Returns:
        A Dash component containing explanation text
    """
    explanation = html.Div(
        [
            html.H4("Understanding the Composition Table"),
            html.P(
                [
                    "This heatmap shows what happens when you ",
                    html.Em("compose"),
                    " two Allen relations. Composition is central to reasoning with temporal intervals.",
                ]
            ),
            html.P(
                [
                    "For example, if we know that interval A is ",
                    html.Strong("before (p)"),
                    " interval B, and B is ",
                    html.Strong("during (d)"),
                    " interval C, what can we say about the relationship between A and C? ",
                    "The composition table gives us the answer: A must be before (p) C.",
                ]
            ),
            html.P(
                [
                    "While some compositions yield a single definite relation (like p ∘ d = p), ",
                    "others result in multiple possibilities (like o ∘ d = {o, p, m}), ",
                    "creating ambiguity in temporal reasoning.",
                ]
            ),
            html.H5("Interpreting the Heatmap"),
            html.P(
                [
                    "Each cell shows what happens when you compose the relation on the y-axis (rel₁) ",
                    "with the relation on the x-axis (rel₂). The color intensity indicates:",
                ]
            ),
            html.Ul(
                [
                    html.Li(
                        [
                            html.Strong("In Cardinality View: "),
                            "The number of possible relations in the result (fewer is more specific)",
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong("In Entropy View: "),
                            "The uncertainty of the result (lower entropy means more certainty)",
                        ]
                    ),
                ]
            ),
            html.P(
                "Try hovering over different cells to see the exact composition results!",
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


def initialize_composition_heatmap():
    """
    Initialize the composition heatmap with default settings.

    Returns:
        Tuple of (composition_data, figure)
    """
    # Compute the composition matrix
    comp_data = create_composition_matrix()
    # Generate the default heatmap (cardinality view)
    fig = generate_interactive_composition_heatmap(comp_data, "cardinality")
    return comp_data, fig


def analysis_of_composition_data(comp_data):
    """
    Provide a statistical analysis of the composition data.

    Args:
        comp_data: Dictionary containing composition data

    Returns:
        Dash components with analysis information
    """
    # Extract data
    cardinality = comp_data["cardinality"].flatten()
    entropy = comp_data["entropy"].flatten()

    # Compute statistics
    avg_cardinality = np.mean(cardinality)
    max_cardinality = np.max(cardinality)
    min_cardinality = np.min(cardinality)

    avg_entropy = np.mean(entropy)
    max_entropy = np.max(entropy)
    min_entropy = np.min(entropy)

    # Find the "most specific" composition (minimum cardinality)
    flat_indices = np.argwhere(comp_data["cardinality"] == min_cardinality)
    most_specific = []
    for idx in flat_indices:
        i, j = idx
        rel1 = ALLEN_RELATION_ORDER[i]
        rel2 = ALLEN_RELATION_ORDER[j]
        result = comp_data["compositions"][(rel1, rel2)]
        most_specific.append(f"{rel1} ∘ {rel2} = {{{', '.join(result)}}}")

    # Find the "most ambiguous" composition (maximum cardinality/entropy)
    flat_indices = np.argwhere(comp_data["cardinality"] == max_cardinality)
    most_ambiguous = []
    for idx in flat_indices:
        i, j = idx
        rel1 = ALLEN_RELATION_ORDER[i]
        rel2 = ALLEN_RELATION_ORDER[j]
        result = comp_data["compositions"][(rel1, rel2)]
        most_ambiguous.append(f"{rel1} ∘ {rel2}")

    # Create analysis panel
    analysis = html.Div(
        [
            html.H4("Composition Table Analysis"),
            html.Div(
                [
                    html.H5("Cardinality Statistics"),
                    html.Table(
                        [
                            html.Tr(
                                [
                                    html.Td(
                                        "Average number of relations per composition:"
                                    ),
                                    html.Td(
                                        f"{avg_cardinality:.2f}",
                                        style={"fontWeight": "bold"},
                                    ),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td("Minimum number (most specific):"),
                                    html.Td(
                                        f"{min_cardinality:.0f}",
                                        style={"fontWeight": "bold"},
                                    ),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td("Maximum number (most ambiguous):"),
                                    html.Td(
                                        f"{max_cardinality:.0f}",
                                        style={"fontWeight": "bold"},
                                    ),
                                ]
                            ),
                        ],
                        style={"width": "100%"},
                    ),
                ],
                style={"marginBottom": "15px"},
            ),
            html.Div(
                [
                    html.H5("Entropy Statistics"),
                    html.Table(
                        [
                            html.Tr(
                                [
                                    html.Td("Average entropy:"),
                                    html.Td(
                                        f"{avg_entropy:.3f} bits",
                                        style={"fontWeight": "bold"},
                                    ),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td("Minimum entropy (most certain):"),
                                    html.Td(
                                        f"{min_entropy:.3f} bits",
                                        style={"fontWeight": "bold"},
                                    ),
                                ]
                            ),
                            html.Tr(
                                [
                                    html.Td("Maximum entropy (most uncertain):"),
                                    html.Td(
                                        f"{max_entropy:.3f} bits",
                                        style={"fontWeight": "bold"},
                                    ),
                                ]
                            ),
                        ],
                        style={"width": "100%"},
                    ),
                ],
                style={"marginBottom": "15px"},
            ),
            html.Div(
                [
                    html.H5("Notable Examples"),
                    html.P(
                        "Most specific compositions (single outcome):",
                        style={"fontWeight": "bold"},
                    ),
                    html.Ul([html.Li(example) for example in most_specific[:3]]),
                    html.P(
                        "Most ambiguous compositions:",
                        style={"fontWeight": "bold"},
                    ),
                    html.Ul(
                        [
                            html.Li(f"{example} (13 possible outcomes)")
                            for example in most_ambiguous[:3]
                        ]
                    ),
                ]
            ),
        ]
    )
    return analysis


if __name__ == "__main__":
    # Test the heatmap generation
    print("Generating composition matrix...")
    comp_data = create_composition_matrix()

    print("Creating test visualizations...")
    fig_card = generate_interactive_composition_heatmap(comp_data, "cardinality")
    fig_ent = generate_interactive_composition_heatmap(comp_data, "entropy")
    # Save HTML visualizations for preview
    import plotly.io as pio

    pio.write_html(fig_card, file="composition_cardinality.html", auto_open=True)
    pio.write_html(fig_ent, file="composition_entropy.html", auto_open=False)

    print("Test visualizations saved as HTML files.")
