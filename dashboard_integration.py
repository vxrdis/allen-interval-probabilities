"""
Allen's Interval Algebra Dashboard Integration

This module integrates the modular visualization components into a complete interactive
dashboard for exploring Allen's interval algebra. It combines:

1. The dashboard shell (layout structure and styles)
2. Animated distribution evolution visualization
3. Interactive composition heatmap visualization
4. Parameter surface visualization

The integration creates a unified interface with shared controls and data stores,
ensuring changes in one component can propagate to others when appropriate.
"""

import time
import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc
import plotly.graph_objects as go
import numpy as np

# Import our modules
from dashboard_shell import create_dashboard_app, STYLES, COLORS
from animated_distribution import (
    run_simulation_in_steps,
    create_distribution_chart,
    create_distribution_animation_controls,
    get_statistical_info,
)
from composition_heatmap import (
    create_composition_matrix,
    generate_interactive_composition_heatmap,
    create_composition_controls,
    create_composition_explanation,
)
from parameter_surface import (
    generate_parameter_surface_data,
    create_3d_surface_plot,
    create_parameter_surface_controls,
    create_parameter_surface_explanation,
)
from constants import ALLEN_RELATION_ORDER, get_relation_name
from simulations import set_random_seed


def create_integrated_dashboard():
    """
    Create and configure the integrated dashboard application with a complete layout structure.

    Returns:
        Configured Dash application ready to run
    """
    # Create a new Dash application with metadata
    app = dash.Dash(
        __name__,
        title="Allen's Interval Algebra Explorer",
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ],
    )

    # Define the complete layout all at once
    app.layout = html.Div(
        id="app-container",
        style={
            "backgroundColor": COLORS["background"],
            "minHeight": "100vh",
            "padding": "20px",
        },
        children=[
            # Header section
            html.Div(
                id="header-section",
                style=STYLES["header"],
                children=[
                    html.H1(
                        "Allen's Interval Algebra Explorer",
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
                id="main-content-wrapper",
                style={"display": "flex", "flexDirection": "row", "gap": "20px"},
                children=[
                    # Side panel for controls and statistics
                    html.Div(
                        id="side-panel",
                        style={"flex": "1", "maxWidth": "300px"},
                        children=[
                            # Simulation Controls
                            html.Div(
                                id="controls-card",
                                style=STYLES["card"],
                                children=[
                                    html.H3(
                                        "Simulation Controls", style={"marginTop": 0}
                                    ),
                                    html.Div(
                                        id="simulation-controls",
                                        children=[
                                            # Birth probability slider
                                            html.Div(
                                                style={"marginBottom": "15px"},
                                                children=[
                                                    html.Label(
                                                        "Birth Probability (pBorn):"
                                                    ),
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
                                                    html.Label(
                                                        "Death Probability (pDie):"
                                                    ),
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
                                                        min=500,
                                                        max=10000,
                                                        step=500,
                                                        value=2000,
                                                        marks={
                                                            500: "500",
                                                            2000: "2k",
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
                                                        min=50,
                                                        max=1000,
                                                        step=50,
                                                        value=200,
                                                        marks={
                                                            50: "50",
                                                            200: "200",
                                                            500: "500",
                                                            1000: "1000",
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
                                                style={
                                                    "backgroundColor": COLORS[
                                                        "primary"
                                                    ],
                                                    "color": "white",
                                                    "border": "none",
                                                    "padding": "10px 20px",
                                                    "borderRadius": "4px",
                                                    "width": "100%",
                                                    "cursor": "pointer",
                                                    "fontWeight": "bold",
                                                },
                                            ),
                                            # Status message area
                                            html.Div(
                                                id="simulation-status",
                                                style={
                                                    "marginTop": "10px",
                                                    "minHeight": "60px",
                                                },
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            # Statistics Panel
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
                            # Visualization-specific controls
                            html.Div(
                                id="viz-controls-card",
                                style=STYLES["card"],
                                children=[
                                    html.H3(
                                        "Visualization Options", style={"marginTop": 0}
                                    ),
                                    html.Div(
                                        id="visualization-controls",
                                        children=[
                                            # Distribution-specific controls
                                            html.Div(
                                                id="distribution-controls",
                                                style={"display": "block"},
                                                children=[
                                                    html.H4(
                                                        "Animation Controls",
                                                        style={
                                                            "marginTop": "0",
                                                            "marginBottom": "15px",
                                                        },
                                                    ),
                                                    html.Label("Animation Speed:"),
                                                    dcc.Slider(
                                                        id="animation-speed",
                                                        min=100,
                                                        max=1000,
                                                        step=100,
                                                        value=500,
                                                        marks={
                                                            100: "Fast",
                                                            500: "Medium",
                                                            1000: "Slow",
                                                        },
                                                        tooltip={
                                                            "placement": "bottom",
                                                            "always_visible": True,
                                                        },
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Button(
                                                                "⏪",
                                                                id="sidebar-restart-animation",
                                                                style={
                                                                    "backgroundColor": "#3498db",
                                                                    "color": "white",
                                                                    "border": "none",
                                                                    "padding": "8px 12px",
                                                                    "borderRadius": "4px",
                                                                    "marginRight": "5px",
                                                                },
                                                            ),
                                                            html.Button(
                                                                "◀",
                                                                id="sidebar-prev-frame",
                                                                style={
                                                                    "backgroundColor": "#3498db",
                                                                    "color": "white",
                                                                    "border": "none",
                                                                    "padding": "8px 12px",
                                                                    "borderRadius": "4px",
                                                                    "marginRight": "5px",
                                                                },
                                                            ),
                                                            html.Button(
                                                                "Play",
                                                                id="sidebar-play-button",
                                                                style={
                                                                    "backgroundColor": "#3498db",
                                                                    "color": "white",
                                                                    "border": "none",
                                                                    "padding": "8px 12px",
                                                                    "borderRadius": "4px",
                                                                    "marginRight": "5px",
                                                                    "minWidth": "60px",
                                                                },
                                                            ),
                                                            html.Button(
                                                                "▶",
                                                                id="sidebar-next-frame",
                                                                style={
                                                                    "backgroundColor": "#3498db",
                                                                    "color": "white",
                                                                    "border": "none",
                                                                    "padding": "8px 12px",
                                                                    "borderRadius": "4px",
                                                                    "marginRight": "5px",
                                                                },
                                                            ),
                                                            html.Button(
                                                                "⏩",
                                                                id="sidebar-end-animation",
                                                                style={
                                                                    "backgroundColor": "#3498db",
                                                                    "color": "white",
                                                                    "border": "none",
                                                                    "padding": "8px 12px",
                                                                    "borderRadius": "4px",
                                                                },
                                                            ),
                                                        ],
                                                        style={
                                                            "marginTop": "15px",
                                                            "display": "flex",
                                                            "justifyContent": "center",
                                                        },
                                                    ),
                                                ],
                                            ),
                                            # Composition-specific controls
                                            html.Div(
                                                id="composition-controls",
                                                style={"display": "none"},
                                                children=create_composition_controls(),
                                            ),
                                            # Surface-specific controls
                                            html.Div(
                                                id="surface-controls",
                                                style={"display": "none"},
                                                children=create_parameter_surface_controls(),
                                            ),
                                        ],
                                    ),
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
                                    # Distribution Evolution Tab
                                    dcc.Tab(
                                        label="Distribution Evolution",
                                        value="distribution-tab",
                                        children=[
                                            html.Div(
                                                style=STYLES["visualization_container"],
                                                id="distribution-container",
                                                children=[
                                                    # Animation info
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
                                                    # Add playback controls here
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
                                                    # Frame information
                                                    html.Div(
                                                        style={
                                                            "marginBottom": "20px",
                                                            "padding": "0 10px",
                                                        },
                                                        children=[
                                                            html.Div(
                                                                style={
                                                                    "display": "flex",
                                                                    "justifyContent": "space-between",
                                                                    "marginBottom": "5px",
                                                                },
                                                                children=[
                                                                    html.Span(
                                                                        "Animation Frame:",
                                                                        style={
                                                                            "fontWeight": "bold"
                                                                        },
                                                                    ),
                                                                    html.Span(
                                                                        id="frame-info",
                                                                        children="0/0",
                                                                    ),
                                                                ],
                                                            ),
                                                            dcc.Slider(
                                                                id="frame-slider",
                                                                min=0,
                                                                max=1,
                                                                step=1,
                                                                value=0,
                                                                marks={},
                                                                tooltip={
                                                                    "placement": "bottom",
                                                                    "always_visible": True,
                                                                },
                                                            ),
                                                        ],
                                                    ),
                                                    # Hidden interval component for automated animation
                                                    dcc.Interval(
                                                        id="animation-interval",
                                                        interval=500,
                                                        disabled=True,
                                                    ),
                                                    # Distribution chart
                                                    dcc.Loading(
                                                        id="loading-distribution",
                                                        type="circle",
                                                        children=[
                                                            dcc.Graph(
                                                                id="distribution-graph"
                                                            )
                                                        ],
                                                    ),
                                                    # Explanation panel
                                                    html.Div(
                                                        children=[
                                                            html.H4(
                                                                "About Allen Relation Evolution"
                                                            ),
                                                            html.P(
                                                                [
                                                                    "This animation shows how the distribution of Allen interval relations evolves ",
                                                                    "as simulation trials increase. The ",
                                                                    html.Span(
                                                                        "red dashed line",
                                                                        style={
                                                                            "color": "red"
                                                                        },
                                                                    ),
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
                                                id="composition-container",
                                                children=[
                                                    create_composition_explanation(),
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
                                                id="surface-container",
                                                children=[
                                                    create_parameter_surface_explanation(),
                                                    # Generate surface button
                                                    html.Div(
                                                        [
                                                            html.Button(
                                                                "Generate Surface",
                                                                id="main-surface-button",
                                                                style={
                                                                    "backgroundColor": COLORS[
                                                                        "primary"
                                                                    ],
                                                                    "color": "white",
                                                                    "border": "none",
                                                                    "padding": "10px 20px",
                                                                    "borderRadius": "4px",
                                                                    "fontSize": "16px",
                                                                    "width": "200px",
                                                                    "cursor": "pointer",
                                                                    "margin": "10px auto 20px auto",
                                                                    "display": "block",
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                    # Status display for surface generation
                                                    html.Div(
                                                        id="surface-status",
                                                        style={
                                                            "margin": "10px 0",
                                                            "textAlign": "center",
                                                        },
                                                    ),
                                                    # Surface visualization
                                                    dcc.Loading(
                                                        id="loading-surface",
                                                        type="circle",
                                                        children=[
                                                            dcc.Graph(
                                                                id="parameter-surface"
                                                            )
                                                        ],
                                                    ),
                                                    # Hidden relation selector container (shown conditionally)
                                                    html.Div(
                                                        id="relation-selector-container",
                                                        style={"display": "none"},
                                                    ),
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
            # Storage elements for data
            html.Div(
                id="storage-container",
                style={"display": "none"},
                children=[
                    dcc.Store(id="simulation-data"),  # For simulation results
                    dcc.Store(id="composition-data"),  # For composition matrix data
                    dcc.Store(id="surface-data"),  # For parameter surface data
                ],
            ),
            # Footer
            html.Footer(
                id="footer",
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

    # Add client-side callback to toggle controls based on active tab
    app.clientside_callback(
        """
        function(active_tab) {
            if (active_tab === 'distribution-tab') {
                return {'display': 'block'}, {'display': 'none'}, {'display': 'none'};
            } else if (active_tab === 'composition-tab') {
                return {'display': 'none'}, {'display': 'block'}, {'display': 'none'};
            } else {
                return {'display': 'none'}, {'display': 'none'}, {'display': 'block'};
            }
        }
        """,
        [
            Output("distribution-controls", "style"),
            Output("composition-controls", "style"),
            Output("surface-controls", "style"),
        ],
        Input("visualization-tabs", "value"),
    )

    # Callback to run simulation and update animation data - adding allow_duplicate=True for frame-slider.value
    @app.callback(
        [
            Output("simulation-data", "data"),
            Output("simulation-status", "children"),
            Output("frame-slider", "max"),
            Output("frame-slider", "marks"),
            Output("frame-slider", "value", allow_duplicate=True),
            Output("animation-info", "children"),
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
        """Run Allen relation simulation and prepare animation data"""
        if n_clicks is None:  # Better handling for initial state
            return {}, "", 0, {}, 0, ""

        # Show running status
        status = html.Div(
            [
                html.P(
                    "Simulation running...",
                    style={"fontWeight": "bold", "color": COLORS["primary"]},
                ),
                html.Div(className="loading-spinner"),
            ]
        )

        # Set random seed for reproducibility
        set_random_seed()

        # Run simulation with step tracking for animation
        start_time = time.time()
        simulation_data = run_simulation_in_steps(pborn, pdie, trials, step_size)
        elapsed_time = time.time() - start_time

        # Create slider marks
        num_frames = len(simulation_data["frames"])
        step = max(1, num_frames // 10)
        marks = {
            i: {"label": f"{simulation_data['frames'][i]['trial_count']}"}
            for i in range(0, num_frames, step)
        }

        # Always include last frame
        if (num_frames - 1) % step != 0:
            marks[num_frames - 1] = {
                "label": f"{simulation_data['frames'][num_frames - 1]['trial_count']}"
            }

        # Status message
        status = html.Div(
            [
                html.P(
                    [
                        html.I(
                            className="fa fa-check-circle",
                            style={"color": "green", "marginRight": "5px"},
                        ),
                        f"Simulation complete: {trials} trials with pBorn={pborn}, pDie={pdie}",
                    ],
                    style={"fontWeight": "bold"},
                ),
                html.P(
                    f"Generated {num_frames} animation frames in {elapsed_time:.2f} seconds"
                ),
            ]
        )

        # Animation info
        animation_info = f"Allen Relation Distribution (pBorn={pborn}, pDie={pdie})"

        return simulation_data, status, num_frames - 1, marks, 0, animation_info

    # Callback to update distribution chart
    @app.callback(
        Output("distribution-graph", "figure"),
        Input("frame-slider", "value"),
        State("simulation-data", "data"),
        prevent_initial_call=True,
    )
    def update_animation_frame(frame_idx, simulation_data):
        """Update animation based on the selected frame"""
        return create_distribution_chart(simulation_data, frame_idx)

    # Callback to update statistical analysis panel
    @app.callback(
        Output("stats-panel", "children"),
        [Input("frame-slider", "value"), Input("visualization-tabs", "value")],
        State("simulation-data", "data"),
        prevent_initial_call=True,
    )
    def update_stats_panel(frame_idx, active_tab, simulation_data):
        """Update the statistical analysis based on the selected frame and active tab"""
        if active_tab != "distribution-tab":
            # Only show distribution stats on the distribution tab
            return html.P(
                "Select the Distribution Evolution tab to see statistical analysis."
            )

        return get_statistical_info(frame_idx, simulation_data)

    # Combine both animation control callbacks into one
    @app.callback(
        [
            Output("animation-interval", "disabled"),
            Output("animation-interval", "interval"),
            Output("frame-slider", "value", allow_duplicate=True),
            Output("play-button", "children"),
            Output("sidebar-play-button", "children"),
            Output("frame-info", "children", allow_duplicate=True),
        ],
        [
            # Main controls
            Input("play-button", "n_clicks"),
            Input("next-frame", "n_clicks"),
            Input("prev-frame", "n_clicks"),
            Input("restart-animation", "n_clicks"),
            Input("end-animation", "n_clicks"),
            # Sidebar controls
            Input("sidebar-play-button", "n_clicks"),
            Input("sidebar-next-frame", "n_clicks"),
            Input("sidebar-prev-frame", "n_clicks"),
            Input(
                "sidebar-restart-animation", "n_clicks"
            ),  # Fixed: was "sidebar-restart-clicks"
            Input(
                "sidebar-end-animation", "n_clicks"
            ),  # Fixed: was "sidebar-end-clicks"
            # Other inputs
            Input("animation-interval", "n_intervals"),
            Input("animation-speed", "value"),
        ],
        [
            State("frame-slider", "value"),
            State("frame-slider", "max"),
            State("animation-interval", "disabled"),
            State("play-button", "children"),
            State("sidebar-play-button", "children"),
        ],
        prevent_initial_call=True,
    )
    def control_all_animation(
        # Main control clicks
        play_clicks,
        next_clicks,
        prev_clicks,
        restart_clicks,
        end_clicks,
        # Sidebar control clicks
        sidebar_play_clicks,
        sidebar_next_clicks,
        sidebar_prev_clicks,
        sidebar_restart_clicks,
        sidebar_end_clicks,
        # Other inputs
        n_intervals,
        speed_value,
        # States
        current_frame,
        max_frame,
        is_disabled,
        play_label,
        sidebar_play_label,
    ):
        """Control animation playback with all controls"""
        ctx = dash.callback_context
        if not ctx.triggered:
            frame_info = f"{current_frame}/{max_frame}" if max_frame > 0 else "0/0"
            return (
                is_disabled,
                speed_value,
                current_frame,
                play_label,
                sidebar_play_label,
                frame_info,
            )

        # Determine which input triggered the callback
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Handle play/pause buttons from either control set
        if trigger_id in ["play-button", "sidebar-play-button"]:
            # Toggle play state
            new_disabled = not is_disabled
            new_label = "Pause" if not new_disabled else "Play"
            frame_info = f"{current_frame}/{max_frame}" if max_frame > 0 else "0/0"
            return (
                new_disabled,
                speed_value,
                current_frame,
                new_label,
                new_label,
                frame_info,
            )

        # Handle next frame buttons from either control set
        elif trigger_id in ["next-frame", "sidebar-next-frame"]:
            # Go to next frame
            next_frame = min(current_frame + 1, max_frame)
            frame_info = f"{next_frame}/{max_frame}" if max_frame > 0 else "0/0"
            return (
                is_disabled,
                speed_value,
                next_frame,
                play_label,
                sidebar_play_label,
                frame_info,
            )

        # Handle previous frame buttons from either control set
        elif trigger_id in ["prev-frame", "sidebar-prev-frame"]:
            # Go to previous frame
            prev_frame = max(current_frame - 1, 0)
            frame_info = f"{prev_frame}/{max_frame}" if max_frame > 0 else "0/0"
            return (
                is_disabled,
                speed_value,
                prev_frame,
                play_label,
                sidebar_play_label,
                frame_info,
            )

        # Handle restart buttons from either control set
        elif trigger_id in ["restart-animation", "sidebar-restart-animation"]:
            # Go to first frame
            frame_info = f"0/{max_frame}" if max_frame > 0 else "0/0"
            return (
                is_disabled,
                speed_value,
                0,
                play_label,
                sidebar_play_label,
                frame_info,
            )

        # Handle end buttons from either control set
        elif trigger_id in ["end-animation", "sidebar-end-animation"]:
            # Go to last frame
            frame_info = f"{max_frame}/{max_frame}" if max_frame > 0 else "0/0"
            return (
                is_disabled,
                speed_value,
                max_frame,
                play_label,
                sidebar_play_label,
                frame_info,
            )

        elif trigger_id == "animation-interval":
            # Auto-advance frame for animation
            next_frame = current_frame + 1
            if next_frame > max_frame:
                next_frame = 0  # Loop back to beginning
            frame_info = f"{next_frame}/{max_frame}" if max_frame > 0 else "0/0"
            return (
                is_disabled,
                speed_value,
                next_frame,
                play_label,
                sidebar_play_label,
                frame_info,
            )

        elif trigger_id == "animation-speed":
            # Update animation speed
            frame_info = f"{current_frame}/{max_frame}" if max_frame > 0 else "0/0"
            return (
                is_disabled,
                speed_value,
                current_frame,
                play_label,
                sidebar_play_label,
                frame_info,
            )

        # Default: no change
        frame_info = f"{current_frame}/{max_frame}" if max_frame > 0 else "0/0"
        return (
            is_disabled,
            speed_value,
            current_frame,
            play_label,
            sidebar_play_label,
            frame_info,
        )

    # Callback to initialize and update composition heatmap
    @app.callback(
        [Output("composition-data", "data"), Output("composition-heatmap", "figure")],
        [Input("heatmap-view-mode", "value")],
        State("composition-data", "data"),
        prevent_initial_call=False,  # Run on initial load
    )
    def update_composition_heatmap(view_mode, existing_data):
        """Update the composition heatmap based on the selected view mode"""
        # Check if we already have composition data
        if not existing_data:
            # Compute composition data if it doesn't exist
            raw_data = create_composition_matrix()

            # Convert the tuple keys to strings for JSON serialization
            serializable_data = {
                "cardinality": raw_data["cardinality"].tolist(),
                "entropy": raw_data["entropy"].tolist(),
            }

            # Convert tuple keys in compositions to strings
            compositions_dict = {}
            for (rel1, rel2), value in raw_data["compositions"].items():
                # Create a string key like "p,m" from tuple ('p', 'm')
                string_key = f"{rel1},{rel2}"
                compositions_dict[string_key] = value

            serializable_data["compositions"] = compositions_dict
            comp_data = serializable_data
        else:
            comp_data = existing_data

        # Generate the heatmap
        fig = generate_interactive_composition_heatmap(comp_data, view_mode)

        return comp_data, fig

    # Callback for generating parameter surface - fixed duplicate output issue
    @app.callback(
        [
            Output("surface-data", "data"),
            Output("parameter-surface", "figure"),
            Output("surface-status", "children"),
        ],
        Input("main-surface-button", "n_clicks"),
        [
            State("surface-metric", "value"),
            State("surface-relation", "value"),
            State("grid-resolution", "value"),
            State("surface-trials", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_parameter_surface(
        n_clicks, metric, relation, resolution, trials_per_point
    ):
        """Generate and display the parameter surface plot"""
        if n_clicks is None:  # Better handling for initial state
            return None, go.Figure(), ""

        # Show running status
        status = html.Div(
            [
                html.P(
                    "Generating surface...",
                    style={"fontWeight": "bold", "color": COLORS["primary"]},
                )
            ]
        )

        # Default to a resolution value if not provided
        if not resolution or resolution < 3:
            resolution = 7

        if not trials_per_point or trials_per_point < 100:
            trials_per_point = 500

        # Generate values for the parameter grid (from 0.01 to 0.5)
        p_values = np.linspace(0.01, 0.5, resolution)

        # Generate surface data through simulation
        start_time = time.time()
        try:
            surface_data = generate_parameter_surface_data(
                p_values, relation, trials_per_point
            )
            elapsed_time = time.time() - start_time

            # Create the 3D surface plot
            fig = create_3d_surface_plot(surface_data, metric)

            # Create status message
            status = html.Div(
                [
                    html.P(
                        [
                            html.I(
                                className="fa fa-check-circle",
                                style={"color": "green", "marginRight": "5px"},
                            ),
                            "Surface generated successfully",
                        ],
                        style={"fontWeight": "bold"},
                    ),
                    html.P(
                        f"Generated {resolution}×{resolution} grid in {elapsed_time:.2f} seconds"
                    ),
                    html.P(f"Used {trials_per_point} trials per grid point"),
                ]
            )

            return surface_data, fig, status

        except Exception as e:
            # Handle errors gracefully
            status = html.Div(
                [
                    html.P(
                        [
                            html.I(
                                className="fa fa-exclamation-triangle",
                                style={"color": "red", "marginRight": "5px"},
                            ),
                            "Error generating surface",
                        ],
                        style={"fontWeight": "bold", "color": "red"},
                    ),
                    html.P(str(e)),
                ]
            )
            return None, go.Figure(), status

    # Add callback for the relation selector visibility
    app.clientside_callback(
        """
        function(metric_value) {
            if (metric_value === 'probability') {
                return {'display': 'block'};
            } else {
                return {'display': 'none'};
            }
        }
        """,
        Output("relation-selector-container", "style"),
        Input("surface-metric", "value"),
    )

    # Initialize empty parameter surface - adding prevent_initial_call=True
    @app.callback(
        Output("parameter-surface", "figure", allow_duplicate=True),
        Input("visualization-tabs", "value"),
        prevent_initial_call=True,  # Add this to fix the error
    )
    def initialize_surface_plot(tab_value):
        """Create an empty placeholder surface when first switching to the tab"""
        if tab_value != "surface-tab":
            return dash.no_update

        # Create empty figure with instructions
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

    return app


# Add a debug helper function


def debug_simulation(pborn=0.3, pdie=0.3, trials=100):
    """Helper function to debug simulation issues"""
    from simulations import IntervalSimulator

    print(f"Running debug simulation with pBorn={pborn}, pDie={pdie}, trials={trials}")

    # Create simulator
    simulator = IntervalSimulator(pborn, pdie, trials)

    # Run simulation with direct debug tracking
    histories = simulator._simulate_intervals()

    # Check the histories
    print(f"Generated {len(histories)} histories")

    # Check the first few histories
    for i, history in enumerate(histories[:5]):
        print(f"History {i}: {history}")

        # Try to identify relation
        relation = simulator._get_relation_code(history)
        if relation:
            print(f"  Identified as relation: {relation}")
        else:
            print(f"  No relation identified")

    # Run the simulation normally
    results = simulator.simulate()

    # Check results
    total = sum(results.values())
    print(f"Total relations identified: {total} out of {trials} trials")

    # Show distribution
    if total > 0:
        for rel, count in results.items():
            if count > 0:
                print(f"  {rel}: {count} ({count/total:.2%})")
    else:
        print("  No relations were identified!")

    return results


# Add this at the end of your file or in your main section
if __name__ == "__main__":
    debug_simulation()

if __name__ == "__main__":
    print("Initializing Allen's Interval Algebra Interactive Dashboard...")

    # Create the integrated dashboard
    app = create_integrated_dashboard()

    print("Dashboard initialized successfully.")
    print(
        "Starting local server. Open a web browser and navigate to http://127.0.0.1:8050/"
    )

    # Run the server
    app.run_server(debug=True)
