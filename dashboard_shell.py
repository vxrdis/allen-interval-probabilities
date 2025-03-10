"""
Allen's Interval Algebra Dashboard Shell

This module defines the basic structure of an interactive dashboard for exploring Allen's
interval algebra. It creates the layout with tabs for three main visualization types:
1. Animated Distribution Evolution
2. Interactive Composition Table
3. Parameter Space Exploration

The dashboard includes a side panel for controls and statistical analysis, and the main
area for visualizations. This shell serves as the foundation for integrating more complex
interactive visualizations.

Usage:
    Import this module to get the basic dashboard structure, then use the
    integrate_visualisations function to add interactive elements.
"""

import dash
from dash import dcc, html

# Define colour scheme for consistent styling
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

# Define style dictionaries for consistent UI elements
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


def create_dashboard_app(title="Allen's Interval Algebra Explorer"):
    """
    Create a new Dash application with basic structure.

    Args:
        title: Title for the dashboard

    Returns:
        A Dash application instance with basic layout structure
    """
    # Setup the Dash app with metadata
    app = dash.Dash(
        __name__,
        title=title,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ],
    )

    # Define the basic layout
    app.layout = html.Div(
        style={
            "backgroundColor": COLORS["background"],
            "minHeight": "100vh",
            "padding": "20px",
        },
        children=[
            # Header section
            html.Div(
                style=STYLES["header"],
                children=[
                    html.H1(title, style={"textAlign": "center"}),
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
                    # Side panel for controls and statistics
                    html.Div(
                        id="side-panel",
                        style={"flex": "1", "maxWidth": "300px"},
                        children=[
                            # Simulation Controls (placeholder)
                            html.Div(
                                id="controls-card",
                                style=STYLES["card"],
                                children=[
                                    html.H3(
                                        "Simulation Controls", style={"marginTop": 0}
                                    ),
                                    # Controls will be added by integration function
                                    html.Div(id="simulation-controls-placeholder"),
                                ],
                            ),
                            # Statistics Panel (placeholder)
                            html.Div(
                                id="stats-card",
                                style=STYLES["card"],
                                children=[
                                    html.H3(
                                        "Statistical Analysis", style={"marginTop": 0}
                                    ),
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
                            # Visualization-specific controls (placeholder)
                            html.Div(
                                id="viz-controls-card",
                                style=STYLES["card"],
                                children=[
                                    html.H3(
                                        "Visualization Options", style={"marginTop": 0}
                                    ),
                                    # Specific controls will be added by integration function
                                    html.Div(id="visualization-controls-placeholder"),
                                ],
                            ),
                        ],
                    ),
                    # Main visualization area with tabs
                    html.Div(
                        id="main-content",
                        style={"flex": "3"},
                        children=[
                            dcc.Tabs(
                                id="visualization-tabs",
                                value="distribution-tab",  # Default selected tab
                                children=[
                                    # Distribution Evolution Tab (placeholder)
                                    dcc.Tab(
                                        label="Distribution Evolution",
                                        value="distribution-tab",
                                        children=[
                                            html.Div(
                                                style=STYLES["visualization_container"],
                                                id="distribution-container",
                                                children=[
                                                    html.P(
                                                        "Distribution evolution visualization will appear here."
                                                    )
                                                ],
                                            )
                                        ],
                                    ),
                                    # Composition Table Tab (placeholder)
                                    dcc.Tab(
                                        label="Composition Table",
                                        value="composition-tab",
                                        children=[
                                            html.Div(
                                                style=STYLES["visualization_container"],
                                                id="composition-container",
                                                children=[
                                                    html.P(
                                                        "Composition table visualization will appear here."
                                                    )
                                                ],
                                            )
                                        ],
                                    ),
                                    # Parameter Surface Tab (placeholder)
                                    dcc.Tab(
                                        label="Parameter Surface",
                                        value="surface-tab",
                                        children=[
                                            html.Div(
                                                style=STYLES["visualization_container"],
                                                id="surface-container",
                                                children=[
                                                    html.P(
                                                        "Parameter surface visualization will appear here."
                                                    )
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
            # Storage elements for data (placeholders)
            html.Div(
                style={"display": "none"},
                children=[
                    dcc.Store(id="simulation-data"),  # For simulation results
                    dcc.Store(id="composition-data"),  # For composition matrix data
                    dcc.Store(id="surface-data"),  # For parameter surface data
                ],
            ),
            # Footer
            html.Footer(
                children=[
                    html.P("Allen's Interval Algebra Explorer"),
                    html.P(
                        "Based on James F. Allen's 1983 paper and Thomas Alspaugh's notation"
                    ),
                ],
                style={
                    "textAlign": "center",
                    "padding": "20px",
                    "marginTop": "20px",
                    "borderTop": f'1px solid {COLORS["light"]}',
                    "color": "#7f8c8d",
                },
            ),
        ],
    )

    return app


if __name__ == "__main__":
    # Create the basic app shell
    app = create_dashboard_app()

    # Display a message showing this is just the shell
    print("Starting Allen's Interval Algebra Dashboard Shell...")
    print("This is just the basic shell without interactive functionality.")
    print("Import and use the integrate_visualisations function to add interactivity.")

    # Run the server
    app.run_server(debug=True)
