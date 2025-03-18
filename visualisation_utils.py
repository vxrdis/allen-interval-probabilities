"""
Visualization Utilities for Allen's Interval Algebra

This module provides standardized visualization functions that ensure consistent
color schemes and relation ordering across all visualizations in the codebase.
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.graph_objects as go
import dash.html as html
from constants import (
    ALLEN_RELATION_ORDER,
    RELATION_COLOURS,
    RELATION_NAMES,
    get_relation_name,
)
from shared_utils import uniform_distribution_value


def get_relation_color(relation):
    """Get the standard color for a specific Allen relation."""
    return RELATION_COLOURS.get(
        relation, "#333333"
    )  # Default to dark gray if not found


def get_relation_colormap():
    """
    Create a matplotlib colormap from the Allen relation colors.

    Returns:
        Matplotlib colormap with consistent relation colors
    """
    from matplotlib.colors import ListedColormap

    return ListedColormap([RELATION_COLOURS[rel] for rel in ALLEN_RELATION_ORDER])


def create_bar_chart(
    probabilities, title=None, figsize=(12, 6), show_uniform=True, show_labels=True
):
    """
    Create a standardized bar chart visualization of Allen relation probabilities.

    Args:
        probabilities: Dictionary mapping relation codes to probabilities
        title: Chart title
        figsize: Figure size tuple (width, height)
        show_uniform: Whether to show the uniform distribution reference line
        show_labels: Whether to show relation names as text labels

    Returns:
        matplotlib figure and axes
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Ensure we're using the standard relation order
    values = [probabilities.get(rel, 0) for rel in ALLEN_RELATION_ORDER]

    # Create bars with consistent colors
    bars = ax.bar(
        ALLEN_RELATION_ORDER,
        values,
        color=[RELATION_COLOURS[rel] for rel in ALLEN_RELATION_ORDER],
    )

    # Add uniform distribution reference line if requested
    if show_uniform:
        uniform_value = uniform_distribution_value(len(ALLEN_RELATION_ORDER))
        ax.axhline(
            y=uniform_value,
            color="r",
            linestyle="--",
            label=f"Uniform distribution (1/{len(ALLEN_RELATION_ORDER)})",
        )
        ax.legend()

    # Add text labels if requested
    if show_labels:
        for i, rel in enumerate(ALLEN_RELATION_ORDER):
            ax.text(
                i,
                values[i] + max(values) * 0.02,
                get_relation_name(rel),
                ha="center",
                rotation=90,
                fontsize=8,
                color="darkblue",
            )

    # Add labels and title
    ax.set_xlabel("Allen Relations")
    ax.set_ylabel("Probability")
    if title:
        ax.set_title(title)

    # Set reasonable y-axis limits
    ax.set_ylim(0, max(values) * 1.15)

    # Add grid for easier reading
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    return fig, ax


def create_heatmap(matrix_data, title=None, figsize=(12, 10), cmap=None, annot=True):
    """
    Create a standardized heatmap visualization with consistent relation ordering.

    Args:
        matrix_data: 2D data array or dictionary
        title: Heatmap title
        figsize: Figure size tuple (width, height)
        cmap: Optional colormap (defaults to 'viridis')
        annot: Whether to annotate cells with values

    Returns:
        matplotlib figure and axes with seaborn heatmap
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Convert dictionary to numpy array if needed
    if isinstance(matrix_data, dict):
        data_array = np.zeros((len(ALLEN_RELATION_ORDER), len(ALLEN_RELATION_ORDER)))
        for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
            for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
                key = f"{rel1},{rel2}"
                if key in matrix_data:
                    data_array[i, j] = matrix_data[key]
    else:
        data_array = matrix_data

    # Create heatmap with consistent ordering
    sns.heatmap(
        data_array,
        ax=ax,
        cmap=cmap or "viridis",
        xticklabels=ALLEN_RELATION_ORDER,
        yticklabels=ALLEN_RELATION_ORDER,
        annot=annot,
        fmt=".2f" if np.issubdtype(data_array.dtype, np.floating) else "d",
        linewidths=0.5,
    )

    # Add labels and title
    ax.set_xlabel("Second Relation (rel₂)")
    ax.set_ylabel("First Relation (rel₁)")
    if title:
        ax.set_title(title)

    return fig, ax


def create_interactive_heatmap(matrix_data, title=None, height=600, width=800):
    """
    Create an interactive Plotly heatmap with hover tooltips instead of static annotations.

    Args:
        matrix_data: 2D data array or dictionary mapping relation pairs to values
        title: Heatmap title
        height: Figure height in pixels
        width: Figure width in pixels

    Returns:
        Plotly Figure object with interactive heatmap
    """
    # Convert dictionary to numpy array if needed
    if isinstance(matrix_data, dict):
        data_array = np.zeros((len(ALLEN_RELATION_ORDER), len(ALLEN_RELATION_ORDER)))
        for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
            for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
                key = f"{rel1},{rel2}"
                if key in matrix_data:
                    data_array[i, j] = matrix_data[key]
    else:
        data_array = np.array(matrix_data)

    # Create formatted hover text for each cell
    hover_text = []
    for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
        hover_row = []
        for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
            # Format value based on type (float vs int)
            if np.issubdtype(data_array.dtype, np.floating):
                value_str = f"{data_array[i, j]:.4f}"
            else:
                value_str = f"{int(data_array[i, j])}"

            # Create rich tooltip with relation names and value
            hover_row.append(
                f"First relation: {rel1} ({get_relation_name(rel1)})<br>"
                f"Second relation: {rel2} ({get_relation_name(rel2)})<br>"
                f"Value: {value_str}"
            )
        hover_text.append(hover_row)

    # Create color scale based on relation colors
    # For most heatmaps, we'll use a standard color scale
    colorscale = "Viridis"

    # Create the heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=data_array,
            x=ALLEN_RELATION_ORDER,
            y=ALLEN_RELATION_ORDER,
            colorscale=colorscale,
            hoverinfo="text",
            text=hover_text,
        )
    )

    # Update layout with axis labels and title
    fig.update_layout(
        title=title,
        height=height,
        width=width,
        xaxis_title="Second Relation (rel₂)",
        yaxis_title="First Relation (rel₁)",
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(ALLEN_RELATION_ORDER))),
            ticktext=ALLEN_RELATION_ORDER,
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(len(ALLEN_RELATION_ORDER))),
            ticktext=ALLEN_RELATION_ORDER,
        ),
    )

    return fig


def create_composition_heatmap(composition_data, title=None, show_labels=True):
    """
    Create an interactive heatmap specifically for Allen relation compositions.

    Args:
        composition_data: Dictionary mapping relation pairs to lists of resulting relations
        title: Heatmap title
        show_labels: Whether to add text labels showing composition results

    Returns:
        Plotly Figure object with interactive composition heatmap
    """
    # Create array for composition sizes (number of possible relations in each result)
    size_array = np.zeros((len(ALLEN_RELATION_ORDER), len(ALLEN_RELATION_ORDER)))

    # Create array of text labels showing the composition results
    text_array = [
        ["" for _ in range(len(ALLEN_RELATION_ORDER))]
        for _ in range(len(ALLEN_RELATION_ORDER))
    ]

    # Create rich hover text for each cell
    hover_text = []

    # Process composition data
    for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
        hover_row = []
        for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
            key = f"{rel1},{rel2}"
            composition = []

            # Get composition from data if available
            if isinstance(composition_data, dict) and key in composition_data:
                composition = composition_data[key]
            elif (
                isinstance(composition_data, list)
                and i < len(composition_data)
                and j < len(composition_data[i])
            ):
                composition = composition_data[i][j]

            # Count relations in composition
            size = len(composition) if composition else 0
            size_array[i, j] = size

            # Create text representation of composition
            text_array[i][j] = ",".join(composition) if composition else ""

            # Create rich tooltip
            hover_row.append(
                f"{rel1} ∘ {rel2} = {','.join(composition) if composition else '∅'}<br>"
                f"First relation: {rel1} ({get_relation_name(rel1)})<br>"
                f"Second relation: {rel2} ({get_relation_name(rel2)})<br>"
                f"Result contains {size} relation{'s' if size != 1 else ''}"
            )
        hover_text.append(hover_row)

    # Create the heatmap figure
    fig = go.Figure()

    # Add heatmap showing number of relations in each composition
    fig.add_trace(
        go.Heatmap(
            z=size_array,
            x=ALLEN_RELATION_ORDER,
            y=ALLEN_RELATION_ORDER,
            colorscale="YlOrRd",
            hoverinfo="text",
            text=hover_text,
            colorbar=dict(title="Number of Relations"),
        )
    )

    # Add text annotations if requested (can be disabled for cleaner look)
    if show_labels:
        annotations = []
        for i in range(len(ALLEN_RELATION_ORDER)):
            for j in range(len(ALLEN_RELATION_ORDER)):
                annotations.append(
                    dict(
                        x=j,
                        y=i,
                        text=text_array[i][j],
                        showarrow=False,
                        font=dict(size=8, color="black"),
                    )
                )
        fig.update_layout(annotations=annotations)

    # Update layout
    fig.update_layout(
        title=title or "Allen Relation Composition Table",
        height=700,
        width=800,
        xaxis_title="Second Relation (rel₂)",
        yaxis_title="First Relation (rel₁)",
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(ALLEN_RELATION_ORDER))),
            ticktext=ALLEN_RELATION_ORDER,
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(len(ALLEN_RELATION_ORDER))),
            ticktext=ALLEN_RELATION_ORDER,
        ),
    )

    return fig


def create_probability_heatmap(probability_matrix, title=None):
    """
    Create an interactive heatmap for displaying empirical relation probabilities.

    Args:
        probability_matrix: Matrix of probability values
        title: Heatmap title

    Returns:
        Plotly Figure object with interactive probability heatmap
    """
    # Convert to numpy array if needed
    if isinstance(probability_matrix, dict):
        prob_array = np.zeros((len(ALLEN_RELATION_ORDER), len(ALLEN_RELATION_ORDER)))
        for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
            for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
                key = f"{rel1},{rel2}"
                if key in probability_matrix:
                    prob_array[i, j] = probability_matrix[key]
    else:
        prob_array = np.array(probability_matrix)

    # Find most common relation for each cell
    most_common_idx = np.zeros(
        (len(ALLEN_RELATION_ORDER), len(ALLEN_RELATION_ORDER)), dtype=int
    )
    if prob_array.ndim == 3:  # If we have a full distribution for each cell
        for i in range(prob_array.shape[0]):
            for j in range(prob_array.shape[1]):
                most_common_idx[i, j] = np.argmax(prob_array[i, j])

    # Create hover text with detailed probability information
    hover_text = []
    for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
        hover_row = []
        for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
            if prob_array.ndim == 3:  # Full distribution
                most_common = ALLEN_RELATION_ORDER[most_common_idx[i, j]]
                percentage = prob_array[i, j, most_common_idx[i, j]] * 100
                hover_row.append(
                    f"{rel1} ∘ {rel2}<br>"
                    f"Most common: {most_common} ({get_relation_name(most_common)})<br>"
                    f"Probability: {percentage:.1f}%"
                )
            else:  # Simple value
                hover_row.append(
                    f"{rel1} ∘ {rel2}<br>" f"Value: {prob_array[i, j]:.4f}"
                )
        hover_text.append(hover_row)

    # Create a colorful heatmap based on the most common relation
    # Use standard Viridis colormap for typical heatmaps
    colorscale = "Viridis"

    # Create the heatmap
    fig = go.Figure()

    # Add the heatmap layer
    fig.add_trace(
        go.Heatmap(
            z=prob_array if prob_array.ndim == 2 else np.max(prob_array, axis=2),
            x=ALLEN_RELATION_ORDER,
            y=ALLEN_RELATION_ORDER,
            colorscale=colorscale,
            hoverinfo="text",
            text=hover_text,
        )
    )

    # Update layout
    fig.update_layout(
        title=title or "Relation Probability Heatmap",
        height=700,
        width=800,
        xaxis_title="Second Relation (rel₂)",
        yaxis_title="First Relation (rel₁)",
    )

    return fig


# Add standardized UI components and common visualization utilities
def create_control_panel(title, controls, style=None):
    """
    Create a standardized control panel with consistent styling.

    Args:
        title: Title for the control panel
        controls: List of Dash components to include in the panel
        style: Optional additional style dictionary

    Returns:
        A Dash div containing the formatted control panel
    """
    default_style = {
        "padding": "15px",
        "backgroundColor": "#f8f8f8",
        "borderRadius": "5px",
        "marginBottom": "20px",
    }

    if style:
        default_style.update(style)

    return html.Div(
        [html.H4(title, style={"marginTop": "0", "marginBottom": "15px"}), *controls],
        style=default_style,
    )


def create_explanation_panel(title, content, style=None):
    """
    Create a standardized explanation panel with consistent styling.

    Args:
        title: Title for the explanation panel
        content: List of Dash components for the panel content
        style: Optional additional style dictionary

    Returns:
        A Dash div containing the formatted explanation panel
    """
    default_style = {
        "margin": "20px 0",
        "padding": "15px",
        "backgroundColor": "#f8f8f8",
        "borderRadius": "5px",
    }

    if style:
        default_style.update(style)

    return html.Div([html.H4(title), *content], style=default_style)


def create_colorscale_for_relation(relation):
    """
    Create a colorscale that transitions from white to the relation's color.

    Args:
        relation: Allen relation code

    Returns:
        List of color stops for a plotly colorscale
    """
    color = RELATION_COLOURS.get(relation, "#333333")
    return [[0, "white"], [1, color]]


def generate_heatmap_figure(
    z_data,
    x_labels=None,
    y_labels=None,
    hover_text=None,
    colorscale="Viridis",
    title=None,
    x_title="Second Relation (rel₂)",
    y_title="First Relation (rel₁)",
    colorbar_title=None,
    height=700,
    width=800,
):
    """
    Generate a standardized heatmap visualization using Plotly.

    Args:
        z_data: 2D array of values for the heatmap
        x_labels: Labels for x-axis (default: Allen relation order)
        y_labels: Labels for y-axis (default: Allen relation order)
        hover_text: Custom hover text matrix (optional)
        colorscale: Colorscale to use
        title: Chart title
        x_title: X-axis title
        y_title: Y-axis title
        colorbar_title: Title for the colorbar
        height: Figure height in pixels
        width: Figure width in pixels

    Returns:
        Plotly Figure object
    """
    # Use Allen relation order as default labels if none provided
    if x_labels is None:
        x_labels = ALLEN_RELATION_ORDER
    if y_labels is None:
        y_labels = ALLEN_RELATION_ORDER

    # Create heatmap trace
    heatmap_args = {
        "z": z_data,
        "x": x_labels,
        "y": y_labels,
        "colorscale": colorscale,
        "showscale": True,
    }

    if colorbar_title:
        heatmap_args["colorbar"] = dict(title=dict(text=colorbar_title))

    if hover_text is not None:
        heatmap_args["hoverinfo"] = "text"
        heatmap_args["text"] = hover_text

    # Create the figure
    fig = go.Figure(data=go.Heatmap(**heatmap_args))

    # Update layout
    layout = {
        "xaxis_title": x_title,
        "yaxis_title": y_title,
        "height": height,
        "width": width,
    }

    if title:
        layout["title"] = title

    fig.update_layout(**layout)

    return fig


def generate_3d_surface_figure(
    x_data,
    y_data,
    z_data,
    colorscale="Viridis",
    title=None,
    x_title="X Axis",
    y_title="Y Axis",
    z_title="Z Axis",
    colorbar_title=None,
    height=700,
    width=900,
):
    """
    Generate a standardized 3D surface visualization using Plotly.

    Args:
        x_data: Values for x-axis
        y_data: Values for y-axis
        z_data: 2D array of values for z-axis
        colorscale: Colorscale to use
        title: Chart title
        x_title: X-axis title
        y_title: Y-axis title
        z_title: Z-axis title
        colorbar_title: Title for the colorbar
        height: Figure height in pixels
        width: Figure width in pixels

    Returns:
        Plotly Figure object
    """
    # Create surface trace
    surface_args = {
        "x": x_data,
        "y": y_data,
        "z": z_data,
        "colorscale": colorscale,
    }

    if colorbar_title:
        surface_args["colorbar"] = dict(title=colorbar_title)

    # Create the figure
    fig = go.Figure(data=[go.Surface(**surface_args)])

    # Update layout
    fig.update_layout(
        title=title,
        height=height,
        width=width,
        scene=dict(
            xaxis_title=x_title,
            yaxis_title=y_title,
            zaxis_title=z_title,
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
            aspectratio=dict(x=1, y=1, z=0.7),
        ),
        margin=dict(l=65, r=50, b=65, t=90),
    )

    return fig


def run_visualization_demo():
    """
    Run a demonstration of the various visualization utilities.

    This function creates sample visualizations using all the available
    visualization functions in this module and saves them to files.
    """
    import plotly.io as pio
    from relations import compose_relations

    print("Running visualization utilities demonstration...")

    # Generate sample probability data
    sample_probs = {rel: np.random.random() for rel in ALLEN_RELATION_ORDER}
    # Normalize to create a proper probability distribution
    total = sum(sample_probs.values())
    sample_probs = {rel: val / total for rel, val in sample_probs.items()}

    # 1. Create static bar chart
    print("Creating bar chart...")
    fig, ax = create_bar_chart(sample_probs, "Sample Allen Relation Distribution")
    plt.savefig("demo_bar_chart.png")
    plt.close(fig)

    # 2. Generate composition data for heatmaps
    print("Generating composition data...")
    composition_dict = {}
    for rel1 in ALLEN_RELATION_ORDER:
        for rel2 in ALLEN_RELATION_ORDER:
            composition = compose_relations(rel1, rel2)
            composition_dict[f"{rel1},{rel2}"] = composition

    # 3. Create static heatmap
    print("Creating static heatmap...")
    # Create a simple matrix for demonstration
    size_matrix = np.zeros((len(ALLEN_RELATION_ORDER), len(ALLEN_RELATION_ORDER)))
    for i, rel1 in enumerate(ALLEN_RELATION_ORDER):
        for j, rel2 in enumerate(ALLEN_RELATION_ORDER):
            key = f"{rel1},{rel2}"
            size_matrix[i, j] = (
                len(composition_dict[key]) if key in composition_dict else 0
            )

    fig, ax = create_heatmap(size_matrix, "Composition Size Matrix")
    plt.savefig("demo_static_heatmap.png")
    plt.close(fig)

    # 4. Create interactive heatmaps
    print("Creating interactive heatmaps...")
    # Simple interactive heatmap
    simple_fig = create_interactive_heatmap(
        size_matrix, "Interactive Composition Size Matrix"
    )
    pio.write_html(simple_fig, file="demo_interactive_heatmap.html")

    # Composition heatmap with annotations
    comp_fig = create_composition_heatmap(
        composition_dict, "Allen Relation Composition Table", show_labels=True
    )
    pio.write_html(comp_fig, file="demo_composition_heatmap.html")

    # Composition heatmap without annotations
    comp_fig_clean = create_composition_heatmap(
        composition_dict, "Allen Relation Composition Table (Clean)", show_labels=False
    )
    pio.write_html(comp_fig_clean, file="demo_composition_heatmap_clean.html")

    # 5. Create probability heatmap
    print("Creating probability heatmap...")
    # Generate sample probability matrix
    prob_matrix = np.zeros((len(ALLEN_RELATION_ORDER), len(ALLEN_RELATION_ORDER)))
    for i in range(len(ALLEN_RELATION_ORDER)):
        for j in range(len(ALLEN_RELATION_ORDER)):
            prob_matrix[i, j] = np.random.random()

    prob_fig = create_probability_heatmap(prob_matrix, "Sample Probability Heatmap")
    pio.write_html(prob_fig, file="demo_probability_heatmap.html")

    print("Demo complete! Files saved in the current directory.")

    return {
        "static_files": ["demo_bar_chart.png", "demo_static_heatmap.png"],
        "interactive_files": [
            "demo_interactive_heatmap.html",
            "demo_composition_heatmap.html",
            "demo_composition_heatmap_clean.html",
            "demo_probability_heatmap.html",
        ],
    }


if __name__ == "__main__":
    # Run the demo if this file is executed directly
    run_visualization_demo()
