import dash
from dash import dcc, html, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import json
import math
from plotly.subplots import make_subplots
from datetime import datetime
import plotly.io as pio
import base64
from io import BytesIO
from fractions import Fraction
import os
import io
import re

# Import required functions and constants
from simulations import arSimulate
from stats import entropy, gini, describe_global, js_divergence
from constants import (
    ALLEN_RELATIONS,
    UNIFORM_DISTRIBUTION,
    FERNANDO_VOGEL_DISTRIBUTION,
    SULIMAN_DISTRIBUTION,
    RELATION_NAMES,
    RELATION_COLORS,
)
from comp_runner import generate_valid_triples, build_composition_table
from reference_tables import get_reference_tables

# Initialize the Dash app with Bootstrap styling
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

# Add this line to expose the Flask server for Gunicorn
server = app.server


# Helper function for number formatting
def format_number(val, digits=4):
    if val is None:
        return "N/A"
    if isinstance(val, float):
        if math.isnan(val):
            return "NaN"
        if math.isinf(val):
            return "∞" if val > 0 else "-∞"
        return f"{val:.{digits}f}"
    return str(val)


# Calculate standard deviation of distribution
def calc_stddev(distribution):
    values = np.array(list(distribution.values()))
    return np.std(values) * len(values)


# Find the mode of a distribution
def find_mode(distribution):
    if not distribution:
        return None
    max_val = max(distribution.values())
    for rel, val in distribution.items():
        if val == max_val:
            return rel
    return None


# Convert a percentage to a simplified fraction representation
def percentage_to_fraction(percentage, max_denominator=30):
    """Convert a percentage to a simplified fraction representation."""
    if percentage == 100:
        return "-"  # Use dash for 100% (single outcome)

    decimal = percentage / 100
    frac = Fraction(decimal).limit_denominator(max_denominator)
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


# Function to generate all 13×13 compositions
def generate_full_composition_matrix(p_born, p_die, trials, limit_per_cell):
    """Generate a full 13×13 composition matrix for all Allen relations"""
    # First generate the triples with the simulation parameters
    triples = generate_valid_triples(p_born, p_die, trials, limit_per_cell)

    # Build the composition table from the generated triples
    table = build_composition_table(triples)

    # Initialize the results matrix
    matrix = {}

    # Track global distribution of R3 outcomes across all compositions
    global_r3_counts = {}

    # For each pair of relations, extract the composition results
    for r1 in ALLEN_RELATIONS:
        matrix[r1] = {}
        for r2 in ALLEN_RELATIONS:
            composition = table.get(r1, {}).get(r2, {})
            if composition:
                total = sum(composition.values())
                matrix[r1][r2] = {
                    "composition": {
                        rel: {
                            "count": count,
                            "percentage": (count / total * 100) if total > 0 else 0,
                        }
                        for rel, count in composition.items()
                    },
                    "total": total,
                }

                # Add to global distribution counts
                for rel, count in composition.items():
                    global_r3_counts[rel] = global_r3_counts.get(rel, 0) + count
            else:
                matrix[r1][r2] = {"composition": {}, "total": 0}

    # Calculate global statistics
    global_total = sum(global_r3_counts.values())
    global_distribution = (
        {rel: count / global_total for rel, count in global_r3_counts.items()}
        if global_total > 0
        else {}
    )

    # Calculate metrics
    global_entropy = entropy(global_distribution)
    global_gini = gini(global_distribution)
    global_coverage = sum(1 for val in global_distribution.values() if val > 0)

    # Calculate JS divergence against theoretical models
    js_uniform = js_divergence(global_distribution, UNIFORM_DISTRIBUTION)
    js_fv = js_divergence(global_distribution, FERNANDO_VOGEL_DISTRIBUTION)
    js_suliman = js_divergence(global_distribution, SULIMAN_DISTRIBUTION)

    # Determine best fit model
    min_js = min(js_uniform, js_fv, js_suliman)
    if min_js == js_uniform:
        best_fit = "Uniform"
        best_fit_js = js_uniform
    elif min_js == js_fv:
        best_fit = "Fernando-Vogel"
        best_fit_js = js_fv
    else:
        best_fit = "Suliman"
        best_fit_js = js_suliman

    # Mode (most common relation)
    mode_relation = (
        max(global_distribution.items(), key=lambda x: x[1])[0]
        if global_distribution
        else None
    )

    global_stats = {
        "distribution": global_distribution,
        "raw_counts": global_r3_counts,
        "entropy": global_entropy,
        "gini": global_gini,
        "coverage": global_coverage,
        "js_uniform": js_uniform,
        "js_fv": js_fv,
        "js_suliman": js_suliman,
        "best_fit": best_fit,
        "best_fit_js": best_fit_js,
        "mode": mode_relation,
        "mode_name": (
            RELATION_NAMES.get(mode_relation, "Unknown") if mode_relation else "N/A"
        ),
    }

    return matrix, len(triples), global_stats


# Create the layout with a more compact header and improved styling with proper edge alignment
app.layout = dbc.Container(
    [
        # Redesigned compact header section with properly aligned right edges
        dbc.Row(
            [
                # Left side - Title
                dbc.Col(
                    html.H2(
                        "Probabilities of Allen Interval Relations", className="mt-3"
                    ),
                    md=5,
                ),
                # Right side - With consistent right alignment that matches other containers
                dbc.Col(
                    [
                        # Badges with better spacing and alignment
                        html.Div(
                            [
                                html.A(
                                    html.Img(
                                        src="https://img.shields.io/badge/License-MIT-yellow.svg",
                                        alt="MIT License",
                                    ),
                                    href="https://github.com/vxrdis/allen-interval-probabilities/blob/main/LICENSE",
                                    className="d-inline-block mx-2",
                                    style={"textDecoration": "none"},
                                ),
                                html.A(
                                    html.Img(
                                        src="https://img.shields.io/badge/Python-3.9-blue.svg",
                                        alt="Python 3.9",
                                    ),
                                    href="https://www.python.org/downloads/release/python-396/",
                                    className="d-inline-block mx-2",
                                    style={"textDecoration": "none"},
                                ),
                                html.A(
                                    html.Img(
                                        src="https://img.shields.io/github/last-commit/vxrdis/allen-interval-probabilities",
                                        alt="Last Commit",
                                    ),
                                    href="https://github.com/vxrdis/allen-interval-probabilities/commits/main",
                                    className="d-inline-block mx-2",
                                    style={"textDecoration": "none"},
                                ),
                                html.A(
                                    html.Img(
                                        src="https://img.shields.io/github/repo-size/vxrdis/allen-interval-probabilities",
                                        alt="Repo Size",
                                    ),
                                    href="https://github.com/vxrdis/allen-interval-probabilities",
                                    className="d-inline-block mx-2",
                                    style={"textDecoration": "none"},
                                ),
                                html.A(
                                    html.Img(
                                        src="https://img.shields.io/badge/code%20style-black-000000.svg",
                                        alt="Code Style: Black",
                                    ),
                                    href="https://black.readthedocs.io/en/stable/",
                                    className="d-inline-block mx-2",
                                    style={"textDecoration": "none"},
                                ),
                            ],
                            # Remove horizontal padding/margin on the right side
                            className="d-flex justify-content-end flex-wrap mb-2 pr-0",
                            style={"paddingRight": "0", "marginRight": "0"},
                        ),
                        # Project info with improved alignment
                        html.Div(
                            [
                                html.Small(
                                    [
                                        "A ",
                                        html.A(
                                            "Final Year Project",
                                            href="https://projects.scss.tcd.ie",
                                            target="_blank",
                                            rel="noopener noreferrer",
                                            className="text-decoration-none",
                                            style={
                                                "color": "#007bff",
                                                "fontWeight": "500",
                                            },
                                        ),
                                        " by ",
                                        html.Strong("Cillín Forrester"),
                                        " under supervision of Dr ",
                                        html.A(
                                            "Tim Fernando",
                                            href="https://www.scss.tcd.ie/Tim.Fernando/",
                                            target="_blank",
                                            rel="noopener noreferrer",
                                            className="text-decoration-none",
                                            style={
                                                "color": "#007bff",
                                                "fontWeight": "500",
                                            },
                                        ),
                                        ", ",
                                        html.A(
                                            "School of Computer Science and Statistics",
                                            href="https://www.tcd.ie/scss/",
                                            target="_blank",
                                            rel="noopener noreferrer",
                                            className="text-decoration-none",
                                            style={
                                                "color": "#007bff",
                                                "fontWeight": "500",
                                            },
                                        ),
                                    ],
                                    className="text-muted",
                                ),
                            ],
                            # Remove horizontal padding/margin on the right side
                            className="d-flex justify-content-end pr-0",
                            style={"paddingRight": "0", "marginRight": "0"},
                        ),
                    ],
                    md=7,
                    # Fix the column padding to match the card containers
                    className="px-3",  # Match Bootstrap's default card padding
                ),
            ],
            # Match the row padding to the card containers
            className="border-bottom pb-2 mb-3 mx-0",
            style={"marginRight": "0"},
        ),
        # Add tab navigation with renamed tabs
        dbc.Tabs(
            [
                dbc.Tab(
                    # This tab contains all the existing main content
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Simulation Parameters"),
                                            dbc.CardBody(
                                                [
                                                    # Birth probability with slider and precise input field
                                                    html.Label(
                                                        "Birth Probability (pBorn):"
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                dcc.Slider(
                                                                    id="p-born-slider",
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.05,
                                                                    value=0.5,
                                                                    marks={
                                                                        i
                                                                        / 10: f"{i/10:.1f}"
                                                                        for i in range(
                                                                            11
                                                                        )
                                                                    },
                                                                    tooltip={
                                                                        "placement": "bottom",
                                                                        "always_visible": True,
                                                                    },
                                                                ),
                                                                width=9,
                                                            ),
                                                            dbc.Col(
                                                                dbc.Input(
                                                                    id="p-born-input",
                                                                    type="number",
                                                                    value=0.5,
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.0001,  # Changed from 0.1 to 0.001
                                                                    style={
                                                                        "height": "38px"
                                                                    },
                                                                ),
                                                                width=3,
                                                            ),
                                                        ],
                                                        className="mb-3 align-items-center",
                                                    ),
                                                    # Death probability with slider and precise input field
                                                    html.Label(
                                                        "Death Probability (pDie):"
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                dcc.Slider(
                                                                    id="p-die-slider",
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.05,
                                                                    value=0.5,
                                                                    marks={
                                                                        i
                                                                        / 10: f"{i/10:.1f}"
                                                                        for i in range(
                                                                            11
                                                                        )
                                                                    },
                                                                    tooltip={
                                                                        "placement": "bottom",
                                                                        "always_visible": True,
                                                                    },
                                                                ),
                                                                width=9,
                                                            ),
                                                            dbc.Col(
                                                                dbc.Input(
                                                                    id="p-die-input",
                                                                    type="number",
                                                                    value=0.5,
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.0001,  # Changed from 0.1 to 0.001
                                                                    style={
                                                                        "height": "38px"
                                                                    },
                                                                ),
                                                                width=3,
                                                            ),
                                                        ],
                                                        className="mb-3 align-items-center",
                                                    ),
                                                    # Small helper text for precise value input
                                                    html.Small(
                                                        "Use input fields for precise values (e.g. 0.001)",
                                                        className="text-muted d-block mb-3",
                                                    ),
                                                    html.Label("Number of Trials:"),
                                                    dbc.Input(
                                                        id="trials-input",
                                                        type="number",
                                                        min=100,
                                                        step=100,
                                                        value=100000,
                                                        className="mb-4",
                                                    ),
                                                    dbc.Button(
                                                        "Run Simulation",
                                                        id="run-button",
                                                        color="primary",
                                                        size="lg",
                                                        className="w-100 mb-2",
                                                    ),
                                                    dbc.Button(
                                                        "Export Results as CSV",
                                                        id="export-csv-button",
                                                        color="secondary",
                                                        size="sm",
                                                        className="w-100 mt-2",
                                                    ),
                                                    dbc.Button(
                                                        "Export Results as JSON",
                                                        id="export-json-button",
                                                        color="info",
                                                        size="sm",
                                                        className="w-100 mt-2",
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Simulation History"),
                                            dbc.CardBody(
                                                [
                                                    html.Div(id="history-summary"),
                                                    html.P(
                                                        "Total runs: ",
                                                        className="mb-0 mt-2 font-weight-bold",
                                                    ),
                                                    html.Span(
                                                        id="total-runs", children="0"
                                                    ),
                                                    html.P(
                                                        "Last run: ",
                                                        className="mb-0 mt-2 font-weight-bold",
                                                    ),
                                                    html.Span(
                                                        id="last-run-time",
                                                        children="None",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Hr(className="my-2"),
                                                            html.P(
                                                                "Model Fit Analysis:",
                                                                className="mb-0 mt-2 font-weight-bold",
                                                            ),
                                                            dbc.Alert(
                                                                id="best-fit-detail",
                                                                color="info",
                                                                className="mt-1 p-2",
                                                                children="No simulation yet",
                                                            ),
                                                        ],
                                                        className="mt-2",
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="mt-3",
                                    ),
                                    # Add the entropy heatmap below Simulation History
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Entropy Heatmap"),
                                            dbc.CardBody(
                                                [
                                                    html.P(
                                                        "Heat map shows entropy across parameter space",
                                                        className="text-muted small mb-2",
                                                    ),
                                                    dcc.Graph(
                                                        id="entropy-heatmap",
                                                        config={
                                                            "displayModeBar": False
                                                        },
                                                        style={"height": "250px"},
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="mt-3",
                                    ),
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.Label(
                                                        "Max denominator for fraction display:"
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                dcc.Slider(
                                                                    id="max-denominator-slider",
                                                                    min=2,
                                                                    max=100,
                                                                    step=1,
                                                                    value=30,
                                                                    marks={
                                                                        i: str(i)
                                                                        for i in range(
                                                                            10, 101, 10
                                                                        )
                                                                    },
                                                                    tooltip={
                                                                        "placement": "bottom",
                                                                        "always_visible": True,
                                                                    },
                                                                ),
                                                                width=9,
                                                            ),
                                                            dbc.Col(
                                                                dbc.Input(
                                                                    id="max-denominator-input",
                                                                    type="number",
                                                                    value=30,
                                                                    min=1,
                                                                    max=1000,
                                                                    step=1,
                                                                    style={
                                                                        "height": "38px"
                                                                    },
                                                                ),
                                                                width=3,
                                                            ),
                                                        ],
                                                        className="mb-3 align-items-center",
                                                    ),
                                                    html.Small(
                                                        "Higher values give more precise fractions but may be harder to read",
                                                        className="text-muted d-block mb-2",
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="mt-3 mb-3",
                                    ),
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Load Previous Results"),
                                            dbc.CardBody(
                                                [
                                                    html.P(
                                                        "Upload previously saved JSON results:"
                                                    ),
                                                    dcc.Upload(
                                                        id="upload-json",
                                                        children=html.Div(
                                                            [
                                                                "Drag and Drop or ",
                                                                html.A("Select File"),
                                                            ]
                                                        ),
                                                        style={
                                                            "width": "100%",
                                                            "height": "60px",
                                                            "lineHeight": "60px",
                                                            "borderWidth": "1px",
                                                            "borderStyle": "dashed",
                                                            "borderRadius": "5px",
                                                            "textAlign": "center",
                                                            "margin-bottom": "10px",
                                                        },
                                                        multiple=False,
                                                        accept="application/json",
                                                    ),
                                                    html.Div(id="upload-json-status"),
                                                    html.Small(
                                                        "Files should be named sim_p[value]_q[value].json",
                                                        className="text-muted d-block mt-2",
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="mt-3 mb-3",
                                    ),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    dbc.Spinner(
                                        children=[
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        "Relation Distribution"
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        html.Label(
                                                                            "Show reference models:",
                                                                            className="font-weight-bold mr-2",
                                                                        ),
                                                                        width="auto",
                                                                    ),
                                                                    dbc.Col(
                                                                        dcc.Checklist(
                                                                            id="model-checklist",
                                                                            options=[
                                                                                {
                                                                                    "label": "Uniform",
                                                                                    "value": "Uniform",
                                                                                },
                                                                                {
                                                                                    "label": "Fernando-Vogel",
                                                                                    "value": "Fernando-Vogel",
                                                                                },
                                                                                {
                                                                                    "label": "Suliman",
                                                                                    "value": "Suliman",
                                                                                },
                                                                            ],
                                                                            value=[],
                                                                            inline=True,
                                                                            className="mb-2",
                                                                            inputStyle={
                                                                                "margin-right": "5px"
                                                                            },
                                                                            labelStyle={
                                                                                "margin-right": "15px"
                                                                            },
                                                                        ),
                                                                    ),
                                                                    # Add sorting checkbox
                                                                    dbc.Col(
                                                                        dcc.Checklist(
                                                                            id="sort-checkbox",
                                                                            options=[
                                                                                {
                                                                                    "label": "Sort relations by frequency",
                                                                                    "value": "sort",
                                                                                }
                                                                            ],
                                                                            value=[],
                                                                            inline=True,
                                                                            className="mb-2",
                                                                            inputStyle={
                                                                                "margin-right": "5px"
                                                                            },
                                                                        ),
                                                                        width=True,
                                                                        className="text-right",
                                                                    ),
                                                                ],
                                                                className="mb-3 d-flex align-items-center",
                                                            ),
                                                            dcc.Graph(
                                                                id="relation-chart"
                                                            ),
                                                            dbc.Row(
                                                                [
                                                                    dbc.Col(
                                                                        html.Div(
                                                                            id="mode-display",
                                                                            className="mt-2 text-muted",
                                                                            style={
                                                                                "font-size": "0.9rem"
                                                                            },
                                                                        ),
                                                                        width="auto",
                                                                    ),
                                                                    dbc.Col(
                                                                        html.Div(
                                                                            dbc.Button(
                                                                                "Export as PNG",
                                                                                id="export-button",
                                                                                color="secondary",
                                                                                className="mt-2",
                                                                            ),
                                                                            className="d-flex justify-content-end",
                                                                        ),
                                                                        width=True,
                                                                    ),
                                                                ],
                                                                className="d-flex justify-content-between align-items-center",
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                className="mb-3",
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dbc.Card(
                                                                [
                                                                    dbc.CardHeader(
                                                                        "Entropy"
                                                                    ),
                                                                    dbc.CardBody(
                                                                        html.H3(
                                                                            id="entropy-value",
                                                                            className="text-center",
                                                                        )
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        md=3,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Card(
                                                                [
                                                                    dbc.CardHeader(
                                                                        "Gini Coefficient"
                                                                    ),
                                                                    dbc.CardBody(
                                                                        html.H3(
                                                                            id="gini-value",
                                                                            className="text-center",
                                                                        )
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        md=3,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Card(
                                                                [
                                                                    dbc.CardHeader(
                                                                        "Std Dev"
                                                                    ),
                                                                    dbc.CardBody(
                                                                        html.H3(
                                                                            id="stddev-value",
                                                                            className="text-center",
                                                                        )
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        md=3,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Card(
                                                                [
                                                                    dbc.CardHeader(
                                                                        "Best Fit"
                                                                    ),
                                                                    dbc.CardBody(
                                                                        html.Div(
                                                                            id="best-fit-value",
                                                                            className="text-center",
                                                                        )
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        md=3,
                                                    ),
                                                ],
                                                className="mb-3",
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dbc.Card(
                                                                [
                                                                    dbc.CardHeader(
                                                                        "JS (Uniform)"
                                                                    ),
                                                                    dbc.CardBody(
                                                                        html.H4(
                                                                            id="js-uniform-value",
                                                                            className="text-center",
                                                                        )
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        md=4,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Card(
                                                                [
                                                                    dbc.CardHeader(
                                                                        "JS (F-V)"
                                                                    ),
                                                                    dbc.CardBody(
                                                                        html.H4(
                                                                            id="js-fv-value",
                                                                            className="text-center",
                                                                        )
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        md=4,
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dbc.Card(
                                                                [
                                                                    dbc.CardHeader(
                                                                        "JS (Suliman)"
                                                                    ),
                                                                    dbc.CardBody(
                                                                        html.H4(
                                                                            id="js-suliman-value",
                                                                            className="text-center",
                                                                        )
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        md=4,
                                                    ),
                                                ],
                                                className="mb-3",
                                            ),
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader("Metrics History"),
                                                    dbc.CardBody(
                                                        dcc.Graph(id="metrics-chart")
                                                    ),
                                                ],
                                                className="mb-3",
                                            ),
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader("Detailed Results"),
                                                    dbc.CardBody(
                                                        dash_table.DataTable(
                                                            id="results-table",
                                                            columns=[
                                                                {
                                                                    "name": "Relation",
                                                                    "id": "relation",
                                                                },
                                                                {
                                                                    "name": "Name",
                                                                    "id": "name",
                                                                },
                                                                {
                                                                    "name": "Count",
                                                                    "id": "count",
                                                                },
                                                                {
                                                                    "name": "Probability",
                                                                    "id": "probability",
                                                                },
                                                                {
                                                                    "name": "≈ Fraction",
                                                                    "id": "fraction",
                                                                },
                                                            ],
                                                            style_table={
                                                                "overflowX": "auto"
                                                            },
                                                            style_cell={
                                                                "textAlign": "left",
                                                                "padding": "8px",
                                                            },
                                                            style_header={
                                                                "backgroundColor": "#f8f9fa",
                                                                "fontWeight": "bold",
                                                            },
                                                            style_data_conditional=[
                                                                {
                                                                    "if": {
                                                                        "state": "selected"
                                                                    },
                                                                    "backgroundColor": "#e6f2ff",
                                                                    "border": "1px solid #ccc",
                                                                }
                                                            ],
                                                        )
                                                    ),
                                                ]
                                            ),
                                        ],
                                        id="loading-spinner",
                                        type="border",
                                        fullscreen=False,
                                        color="primary",
                                    )
                                ],
                                md=8,
                            ),
                        ]
                    ),
                    label="Relation Simulation",  # Renamed from "Distribution Simulator"
                    tab_id="tab-simulator",
                    active_label_style={"font-weight": "bold"},
                ),
                dbc.Tab(
                    # Composition Analysis tab - Now only contains single composition analysis
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    # Parameters Card
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Simulation Parameters"),
                                            dbc.CardBody(
                                                [
                                                    # Birth probability with slider and precise input field
                                                    html.Label(
                                                        "Birth Probability (pBorn):"
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                dcc.Slider(
                                                                    id="comp-p-born-slider",
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.05,
                                                                    value=0.5,
                                                                    marks={
                                                                        i
                                                                        / 10: f"{i/10:.1f}"
                                                                        for i in range(
                                                                            11
                                                                        )
                                                                    },
                                                                    tooltip={
                                                                        "placement": "bottom",
                                                                        "always_visible": True,
                                                                    },
                                                                ),
                                                                width=9,
                                                            ),
                                                            dbc.Col(
                                                                dbc.Input(
                                                                    id="comp-p-born-input",
                                                                    type="number",
                                                                    value=0.5,
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.0001,  # Changed from 0.1 to 0.001
                                                                    style={
                                                                        "height": "38px"
                                                                    },
                                                                ),
                                                                width=3,
                                                            ),
                                                        ],
                                                        className="mb-3 align-items-center",
                                                    ),
                                                    # Death probability with slider and precise input field
                                                    html.Label(
                                                        "Death Probability (pDie):"
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                dcc.Slider(
                                                                    id="comp-p-die-slider",
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.05,
                                                                    value=0.5,
                                                                    marks={
                                                                        i
                                                                        / 10: f"{i/10:.1f}"
                                                                        for i in range(
                                                                            11
                                                                        )
                                                                    },
                                                                    tooltip={
                                                                        "placement": "bottom",
                                                                        "always_visible": True,
                                                                    },
                                                                ),
                                                                width=9,
                                                            ),
                                                            dbc.Col(
                                                                dbc.Input(
                                                                    id="comp-p-die-input",
                                                                    type="number",
                                                                    value=0.5,
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.0001,  # Changed from 0.1 to 0.001
                                                                    style={
                                                                        "height": "38px"
                                                                    },
                                                                ),
                                                                width=3,
                                                            ),
                                                        ],
                                                        className="mb-3 align-items-center",
                                                    ),
                                                    # Small helper text for precise value input
                                                    html.Small(
                                                        "Use input fields for precise values (e.g. 0.001)",
                                                        className="text-muted d-block mb-3",
                                                    ),
                                                    html.Label("Number of Trials:"),
                                                    dbc.Input(
                                                        id="comp-trials-input",
                                                        type="number",
                                                        min=1000,
                                                        step=1000,
                                                        value=100000,
                                                        className="mb-3",
                                                    ),
                                                    html.Label("Results Limit:"),
                                                    dbc.Input(
                                                        id="comp-limit-input",
                                                        type="number",
                                                        min=100,
                                                        step=100,
                                                        value=100000,
                                                        className="mb-4",
                                                    ),
                                                    # Relation selection (now directly here, not in tabs)
                                                    html.Div(
                                                        [
                                                            html.Label(
                                                                "Relation 1 (R1):"
                                                            ),
                                                            dcc.Dropdown(
                                                                id="relation1-dropdown",
                                                                options=[
                                                                    {
                                                                        "label": f"{rel} - {RELATION_NAMES[rel]}",
                                                                        "value": rel,
                                                                    }
                                                                    for rel in ALLEN_RELATIONS
                                                                ],
                                                                value=ALLEN_RELATIONS[
                                                                    0
                                                                ],
                                                                clearable=False,
                                                                className="mb-3",
                                                            ),
                                                            html.Label(
                                                                "Relation 2 (R2):"
                                                            ),
                                                            dcc.Dropdown(
                                                                id="relation2-dropdown",
                                                                options=[
                                                                    {
                                                                        "label": f"{rel} - {RELATION_NAMES[rel]}",
                                                                        "value": rel,
                                                                    }
                                                                    for rel in ALLEN_RELATIONS
                                                                ],
                                                                value=ALLEN_RELATIONS[
                                                                    12
                                                                ],
                                                                clearable=False,
                                                                className="mb-4",
                                                            ),
                                                        ],
                                                        className="mt-3",
                                                    ),
                                                    # Run button
                                                    dbc.Button(
                                                        "Run Composition",
                                                        id="run-composition-button",
                                                        color="primary",
                                                        size="lg",
                                                        className="w-100",
                                                    ),
                                                ],
                                            ),
                                        ]
                                    ),
                                    # Results Summary
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Composition Results"),
                                            dbc.CardBody(
                                                [
                                                    html.Div(id="composition-summary"),
                                                    # Styled container with pale green background
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                [
                                                                    html.Strong(
                                                                        "Total valid relations: "
                                                                    ),
                                                                    html.Span(
                                                                        id="comp-valid-count",
                                                                        children="0",
                                                                    ),
                                                                ],
                                                                className="mb-2 text-left",
                                                            ),
                                                            html.Div(
                                                                [
                                                                    html.Strong(
                                                                        "Most common result: "
                                                                    ),
                                                                    html.Span(
                                                                        id="comp-most-common",
                                                                        children="None",
                                                                    ),
                                                                ],
                                                                className="mb-1 text-left",
                                                            ),
                                                        ],
                                                        className="mt-3 p-3 rounded",
                                                        style={
                                                            "backgroundColor": "#e8f5e9",  # Pale green
                                                            "border": "1px solid #c8e6c9",
                                                            "textAlign": "left",
                                                        },
                                                    ),
                                                ],
                                            ),
                                        ],
                                        className="mt-3",
                                    ),
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.Label(
                                                        "Max denominator for fraction display:"
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                dcc.Slider(
                                                                    id="comp-max-denominator-slider",
                                                                    min=2,
                                                                    max=100,
                                                                    step=1,
                                                                    value=30,
                                                                    marks={
                                                                        i: str(i)
                                                                        for i in range(
                                                                            10, 101, 10
                                                                        )
                                                                    },
                                                                    tooltip={
                                                                        "placement": "bottom",
                                                                        "always_visible": True,
                                                                    },
                                                                ),
                                                                width=9,
                                                            ),
                                                            dbc.Col(
                                                                dbc.Input(
                                                                    id="comp-max-denominator-input",
                                                                    type="number",
                                                                    value=30,
                                                                    min=1,
                                                                    max=1000,
                                                                    step=1,
                                                                    style={
                                                                        "height": "38px"
                                                                    },
                                                                ),
                                                                width=3,
                                                            ),
                                                        ],
                                                        className="mb-3 align-items-center",
                                                    ),
                                                    html.Small(
                                                        "Higher values give more precise fractions but may be harder to read",
                                                        className="text-muted d-block mb-2",
                                                    ),
                                                    html.Small(
                                                        "full = (pmoFDseSdfOMP) and concur = (oFDseSdfO) in order to conserve space",
                                                        className="text-muted d-block mb-2",
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="mt-3 mb-3",
                                    ),
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Load Previous Results"),
                                            dbc.CardBody(
                                                [
                                                    html.P(
                                                        "Upload previously saved JSON results:"
                                                    ),
                                                    dcc.Upload(
                                                        id="upload-comp-json",
                                                        children=html.Div(
                                                            [
                                                                "Drag and Drop or ",
                                                                html.A("Select File"),
                                                            ]
                                                        ),
                                                        style={
                                                            "width": "100%",
                                                            "height": "60px",
                                                            "lineHeight": "60px",
                                                            "borderWidth": "1px",
                                                            "borderStyle": "dashed",
                                                            "borderRadius": "5px",
                                                            "textAlign": "center",
                                                            "margin-bottom": "10px",
                                                        },
                                                        multiple=False,
                                                        accept="application/json",
                                                    ),
                                                    html.Div(
                                                        id="upload-comp-json-status"
                                                    ),
                                                    html.Small(
                                                        "Files should be named comp_p[value]_q[value].json",
                                                        className="text-muted d-block mt-2",
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="mt-3 mb-3",
                                    ),
                                ],
                                md=4,
                                id="composition-left-panel",
                            ),
                            dbc.Col(
                                [
                                    dbc.Spinner(
                                        children=[
                                            # Single composition view
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        id="composition-title",
                                                        children="Select Relations and Run Composition",
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            # Results chart
                                                            dcc.Graph(
                                                                id="composition-chart"
                                                            ),
                                                            # Results table
                                                            html.Div(
                                                                id="composition-table-container",
                                                                className="mt-4",
                                                                children=[
                                                                    html.H5(
                                                                        "Composition Results"
                                                                    ),
                                                                    dash_table.DataTable(
                                                                        id="composition-table",
                                                                        columns=[
                                                                            {
                                                                                "name": "Relation",
                                                                                "id": "relation",
                                                                            },
                                                                            {
                                                                                "name": "Name",
                                                                                "id": "name",
                                                                            },
                                                                            {
                                                                                "name": "Count",
                                                                                "id": "count",
                                                                            },
                                                                            {
                                                                                "name": "Percentage",
                                                                                "id": "percentage",
                                                                            },
                                                                            {
                                                                                "name": "≈ Fraction",
                                                                                "id": "fraction",
                                                                            },
                                                                        ],
                                                                        style_table={
                                                                            "overflowX": "auto"
                                                                        },
                                                                        style_cell={
                                                                            "textAlign": "left",
                                                                            "padding": "8px",
                                                                        },
                                                                        style_header={
                                                                            "backgroundColor": "#f8f9fa",
                                                                            "fontWeight": "bold",
                                                                        },
                                                                        style_data_conditional=[
                                                                            {
                                                                                "if": {
                                                                                    "state": "selected"
                                                                                },
                                                                                "backgroundColor": "#e6f2ff",
                                                                                "border": "1px solid #ccc",
                                                                            }
                                                                        ],
                                                                    ),
                                                                ],
                                                            ),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            # Add reference tables to right panel, below the composition results
                                            html.Div(
                                                [
                                                    html.Hr(className="mt-4"),
                                                    get_reference_tables(),
                                                ],
                                                className="mt-4",
                                                style={"width": "100%"},
                                            ),
                                        ],
                                        id="composition-spinner",
                                        type="border",
                                        fullscreen=False,
                                        color="primary",
                                    )
                                ],
                                md=8,
                            ),
                        ]
                    ),
                    label="Composition Analysis",
                    tab_id="tab-composition",
                    active_label_style={"font-weight": "bold"},
                ),
                # NEW TAB FOR MATRIX ANALYSIS
                dbc.Tab(
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    # Matrix Parameters Card
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Matrix Parameters"),
                                            dbc.CardBody(
                                                [
                                                    # Birth probability with slider and precise input field
                                                    html.Label(
                                                        "Birth Probability (pBorn):"
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                dcc.Slider(
                                                                    id="matrix-p-born-slider",
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.05,
                                                                    value=0.5,
                                                                    marks={
                                                                        i
                                                                        / 10: f"{i/10:.1f}"
                                                                        for i in range(
                                                                            11
                                                                        )
                                                                    },
                                                                    tooltip={
                                                                        "placement": "bottom",
                                                                        "always_visible": True,
                                                                    },
                                                                ),
                                                                width=9,
                                                            ),
                                                            dbc.Col(
                                                                dbc.Input(
                                                                    id="matrix-p-born-input",
                                                                    type="number",
                                                                    value=0.5,
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.0001,  # Changed from 0.1 to 0.001
                                                                    style={
                                                                        "height": "38px"
                                                                    },
                                                                ),
                                                                width=3,
                                                            ),
                                                        ],
                                                        className="mb-3 align-items-center",
                                                    ),
                                                    # Death probability with slider and precise input field
                                                    html.Label(
                                                        "Death Probability (pDie):"
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                dcc.Slider(
                                                                    id="matrix-p-die-slider",
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.05,
                                                                    value=0.5,
                                                                    marks={
                                                                        i
                                                                        / 10: f"{i/10:.1f}"
                                                                        for i in range(
                                                                            11
                                                                        )
                                                                    },
                                                                    tooltip={
                                                                        "placement": "bottom",
                                                                        "always_visible": True,
                                                                    },
                                                                ),
                                                                width=9,
                                                            ),
                                                            dbc.Col(
                                                                dbc.Input(
                                                                    id="matrix-p-die-input",
                                                                    type="number",
                                                                    value=0.5,
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.0001,  # Changed from 0.1 to 0.001
                                                                    style={
                                                                        "height": "38px"
                                                                    },
                                                                ),
                                                                width=3,
                                                            ),
                                                        ],
                                                        className="mb-3 align-items-center",
                                                    ),
                                                    # Small helper text for precise value input
                                                    html.Small(
                                                        "Use input fields for precise values (e.g. 0.001)",
                                                        className="text-muted d-block mb-3",
                                                    ),
                                                    html.Label("Number of Trials:"),
                                                    dbc.Input(
                                                        id="matrix-trials-input",
                                                        type="number",
                                                        min=1000,
                                                        step=1000,
                                                        value=100000,
                                                        className="mb-3",
                                                    ),
                                                    html.Label("Results Limit:"),
                                                    dbc.Input(
                                                        id="matrix-limit-input",
                                                        type="number",
                                                        min=100,
                                                        step=100,
                                                        value=100000,
                                                        className="mb-4",
                                                    ),
                                                    html.Small(
                                                        "full=(pmoFDseSdfOMP) and concur=(oFDseSdfO)",
                                                        className="text-muted d-block mb-3",
                                                    ),
                                                    # Run button
                                                    dbc.Button(
                                                        "Calculate Full Matrix",
                                                        id="run-matrix-button",
                                                        color="primary",
                                                        size="lg",
                                                        className="w-100 mt-4",
                                                    ),
                                                ],
                                            ),
                                        ]
                                    ),
                                    # Matrix Results Status Card
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Matrix Status"),
                                            dbc.CardBody(
                                                html.Div(
                                                    id="matrix-status", className="mt-0"
                                                )
                                            ),
                                        ],
                                        className="mt-3",
                                    ),
                                    # Global Statistics Card (moved from right panel)
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Global Statistics"),
                                            dbc.CardBody(
                                                html.Div(
                                                    id="matrix-global-stats",
                                                    className="p-3 rounded",
                                                    style={
                                                        "backgroundColor": "#e8f5e9",  # Pale green
                                                        "border": "1px solid #c8e6c9",
                                                        "textAlign": "left",
                                                    },
                                                )
                                            ),
                                        ],
                                        className="mt-3 mb-3",
                                    ),
                                    # Fraction denominator control is removed
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Load Previous Results"),
                                            dbc.CardBody(
                                                [
                                                    html.P(
                                                        "Upload previously saved JSON results:"
                                                    ),
                                                    dcc.Upload(
                                                        id="upload-matrix-json",
                                                        children=html.Div(
                                                            [
                                                                "Drag and Drop or ",
                                                                html.A("Select File"),
                                                            ]
                                                        ),
                                                        style={
                                                            "width": "100%",
                                                            "height": "60px",
                                                            "lineHeight": "60px",
                                                            "borderWidth": "1px",
                                                            "borderStyle": "dashed",
                                                            "borderRadius": "5px",
                                                            "textAlign": "center",
                                                            "margin-bottom": "10px",
                                                        },
                                                        multiple=False,
                                                        accept="application/json",
                                                    ),
                                                    html.Div(
                                                        id="upload-matrix-json-status"
                                                    ),
                                                    html.Small(
                                                        "Files should be named comp_p[value]_q[value].json",
                                                        className="text-muted d-block mt-2",
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="mt-3 mb-3",
                                    ),
                                ],
                                md=4,
                                id="matrix-left-panel",
                            ),
                            dbc.Col(
                                [
                                    dbc.Spinner(
                                        children=[
                                            # Matrix view card
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        html.H5(
                                                            "Allen Relation Composition Matrix",
                                                            className="mb-0",
                                                            id="matrix-title",
                                                        )
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            # Global Statistics Card removed from here
                                                            html.P(
                                                                "The matrix shows the composition of Allen relations R1 (rows) with R2 (columns).",
                                                                className="text-muted",
                                                            ),
                                                            html.P(
                                                                [
                                                                    "Hover over cells to see detailed composition results."
                                                                ],
                                                                className="text-muted small",
                                                            ),
                                                            html.Div(
                                                                dcc.Loading(
                                                                    id="loading-matrix",
                                                                    type="default",
                                                                    children=dcc.Graph(
                                                                        id="matrix-heatmap",
                                                                        config={
                                                                            "responsive": True
                                                                        },
                                                                        style={
                                                                            "height": "700px"
                                                                        },
                                                                    ),
                                                                ),
                                                            ),
                                                            html.Div(
                                                                id="cell-details",
                                                                className="mt-3",
                                                            ),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            # Add the two new visualization cards
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        "Entropy Heatmap of Composition Outcomes"
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            html.P(
                                                                "This heatmap shows the entropy (uncertainty) of R3 outcomes for each composition pair.",
                                                                className="text-muted",
                                                            ),
                                                            dcc.Graph(
                                                                id="entropy-composition-heatmap",
                                                                config={
                                                                    "responsive": True
                                                                },
                                                                style={
                                                                    "height": "500px"
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                className="mt-4",
                                            ),
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader(
                                                        "Global R3 Distribution"
                                                    ),
                                                    dbc.CardBody(
                                                        [
                                                            html.P(
                                                                "This chart shows the overall probability of each Allen relation appearing as an R3 outcome across all compositions.",
                                                                className="text-muted",
                                                            ),
                                                            dcc.Graph(
                                                                id="global-r3-distribution",
                                                                config={
                                                                    "responsive": True
                                                                },
                                                                style={
                                                                    "height": "400px"
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                className="mt-4",
                                            ),
                                            # Add reference tables to right panel, below the matrix
                                            html.Div(
                                                [
                                                    html.Hr(className="mt-4"),
                                                    get_reference_tables(),
                                                ],
                                                className="mt-4",
                                                style={"width": "100%"},
                                            ),
                                        ],
                                        id="matrix-spinner",
                                        type="border",
                                        fullscreen=False,
                                        color="primary",
                                    )
                                ],
                                md=8,
                            ),
                        ]
                    ),
                    label="Matrix Analysis",  # New third tab
                    tab_id="tab-matrix",
                    active_label_style={"font-weight": "bold"},
                ),
            ],
            id="tabs",
            active_tab="tab-simulator",
        ),
        dcc.Store(id="simulation-results"),
        dcc.Store(
            id="metrics-history",
            data={
                "runs": [],
                "entropy": [],
                "gini": [],
                "stddev": [],
                "best_fit": [],
                "js_uniform": [],
                "js_fv": [],
                "js_suliman": [],
                "timestamps": [],
                "params": [],
            },
        ),
        # Add a new store for heatmap data
        dcc.Store(
            id="heatmap-data",
            data={
                "p_values": [],
                "q_values": [],
                "entropy_values": [],
                "run_counts": [],
            },
        ),
        dcc.Store(id="download-data"),
        dcc.Download(id="download-png"),
        dcc.Download(id="download-csv"),
        dcc.Download(id="download-json"),
        # Add store for composition results
        dcc.Store(id="composition-results"),
        # Add store for the matrix results
        dcc.Store(id="matrix-results"),
        # Add store for fraction denominator
        dcc.Store(id="fraction-denominator", data=30),
        dcc.Store(id="comp-fraction-denominator", data=30),
        # Add store for matrix fraction denominator (separate from comp)
        dcc.Store(id="matrix-fraction-denominator", data=30),
        # Add store for global distribution download
        dcc.Download(id="download-global-dist"),
    ],
    fluid=True,
    className="p-4",
)


# Replace the four separate callbacks with two combined callbacks that avoid the circular dependency
@app.callback(
    Output("p-born-slider", "value"),
    Output("p-born-input", "value"),
    Output("p-die-slider", "value", allow_duplicate=True),  # Added this output
    Input("p-born-slider", "value"),
    Input("p-born-input", "value"),
    prevent_initial_call=True,
)
def sync_born_inputs(slider_value, input_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "p-born-slider":
        return slider_value, slider_value, dash.no_update
    else:
        return input_value, input_value, dash.no_update


@app.callback(
    Output("p-die-slider", "value"),
    Output("p-die-input", "value"),
    Output("p-born-slider", "value", allow_duplicate=True),  # Added this output
    Input("p-die-slider", "value"),
    Input("p-die-input", "value"),
    prevent_initial_call=True,
)
def sync_die_inputs(slider_value, input_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "p-die-slider":
        return slider_value, slider_value, dash.no_update
    else:
        return input_value, input_value, dash.no_update


@app.callback(
    Output("comp-p-born-slider", "value"),
    Output("comp-p-born-input", "value"),
    Output("comp-p-die-slider", "value", allow_duplicate=True),  # Added this output
    Input("comp-p-born-slider", "value"),
    Input("comp-p-born-input", "value"),
    prevent_initial_call=True,
)
def sync_comp_born_inputs(slider_value, input_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "comp-p-born-slider":
        # When slider changes, update both the input and the die slider
        return dash.no_update, slider_value, slider_value
    else:
        # When input changes, only update the born slider
        return input_value, dash.no_update, dash.no_update


@app.callback(
    Output("comp-p-die-slider", "value"),
    Output("comp-p-die-input", "value"),
    Output("comp-p-born-slider", "value", allow_duplicate=True),  # Added this output
    Input("comp-p-die-slider", "value"),
    Input("comp-p-die-input", "value"),
    prevent_initial_call=True,
)
def sync_comp_die_inputs(slider_value, input_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "comp-p-die-slider":
        # When slider changes, update both the input and the born slider
        return dash.no_update, slider_value, slider_value
    else:
        # When input changes, only update the die slider
        return input_value, dash.no_update, dash.no_update


@app.callback(
    Output("matrix-p-born-slider", "value"),
    Output("matrix-p-born-input", "value"),
    Output("matrix-p-die-slider", "value", allow_duplicate=True),  # Added this output
    Input("matrix-p-born-slider", "value"),
    Input("matrix-p-born-input", "value"),
    prevent_initial_call=True,
)
def sync_matrix_born_inputs(slider_value, input_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "matrix-p-born-slider":
        # When slider changes, update both the input and the die slider
        return dash.no_update, slider_value, slider_value
    else:
        # When input changes, only update the born slider
        return input_value, dash.no_update, dash.no_update


@app.callback(
    Output("matrix-p-die-slider", "value"),
    Output("matrix-p-die-input", "value"),
    Output("matrix-p-born-slider", "value", allow_duplicate=True),  # Added this output
    Input("matrix-p-die-slider", "value"),
    Input("matrix-p-die-input", "value"),
    prevent_initial_call=True,
)
def sync_matrix_die_inputs(slider_value, input_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "matrix-p-die-slider":
        # When slider changes, update both the input and the born slider
        return dash.no_update, slider_value, slider_value
    else:
        # When input changes, only update the die slider
        return input_value, dash.no_update, dash.no_update


@app.callback(
    Output("max-denominator-slider", "value"),
    Output("max-denominator-input", "value"),
    Output("fraction-denominator", "data"),
    Input("max-denominator-slider", "value"),
    Input("max-denominator-input", "value"),
    State("fraction-denominator", "data"),
    prevent_initial_call=True,
)
def sync_max_denominator_inputs(slider_value, input_value, stored_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "max-denominator-slider":
        return dash.no_update, slider_value, slider_value
    else:
        return input_value, dash.no_update, input_value


@app.callback(
    Output("comp-max-denominator-slider", "value"),
    Output("comp-max-denominator-input", "value"),
    Output("comp-fraction-denominator", "data"),
    Input("comp-max-denominator-slider", "value"),
    Input("comp-max-denominator-input", "value"),
    State("comp-fraction-denominator", "data"),
    prevent_initial_call=True,
)
def sync_comp_max_denominator_inputs(slider_value, input_value, stored_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "comp-max-denominator-slider":
        return dash.no_update, slider_value, slider_value
    else:
        return input_value, dash.no_update, input_value


@app.callback(
    Output("matrix-max-denominator-slider", "value"),
    Output("matrix-max-denominator-input", "value"),
    Output("matrix-fraction-denominator", "data"),
    Input("matrix-max-denominator-slider", "value"),
    Input("matrix-max-denominator-input", "value"),
    State("matrix-fraction-denominator", "data"),
    prevent_initial_call=True,
)
def sync_matrix_max_denominator_inputs(slider_value, input_value, stored_value):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "matrix-max-denominator-slider":
        return dash.no_update, slider_value, slider_value
    else:
        return input_value, dash.no_update, input_value


@app.callback(
    Output("simulation-results", "data"),
    Output("loading-spinner", "children", allow_duplicate=True),
    Output("last-run-time", "children"),
    Input("run-button", "n_clicks"),
    State("p-born-input", "value"),  # Use input field value instead of slider
    State("p-die-input", "value"),  # Use input field value instead of slider
    State("trials-input", "value"),
    prevent_initial_call=True,
)
def run_simulation(n_clicks, p_born, p_die, trials):
    if n_clicks is None:
        return {}, dash.no_update, dash.no_update

    counts = arSimulate(p_born, p_die, trials)
    total = sum(counts.values())
    distribution = {
        key: value / total if total > 0 else 0 for key, value in counts.items()
    }

    js_uniform = js_divergence(distribution, UNIFORM_DISTRIBUTION)
    js_fv = js_divergence(distribution, FERNANDO_VOGEL_DISTRIBUTION)
    js_suliman = js_divergence(distribution, SULIMAN_DISTRIBUTION)

    min_js = min(js_uniform, js_fv, js_suliman)
    if min_js == js_uniform:
        best_fit = "Uniform"
        best_fit_js = js_uniform
    elif min_js == js_fv:
        best_fit = "Fernando-Vogel"
        best_fit_js = js_fv
    else:
        best_fit = "Suliman"
        best_fit_js = js_suliman

    mode_relation = find_mode(distribution)
    stddev = calc_stddev(distribution)
    coverage = sum(1 for val in distribution.values() if val > 0)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    results = {
        "distribution": distribution,
        "raw_counts": counts,
        "parameters": {"p_born": p_born, "p_die": p_die, "trials": trials},
        "stats": {
            "mode": mode_relation,
            "mode_name": RELATION_NAMES.get(mode_relation, "Unknown"),
            "stddev": stddev,
            "coverage": coverage,
            "best_fit": best_fit,
            "best_fit_js": best_fit_js,
            "js_uniform": js_uniform,
            "js_fv": js_fv,
            "js_suliman": js_suliman,
            "timestamp": timestamp,
        },
    }
    return results, dash.no_update, timestamp


@app.callback(
    Output("relation-chart", "figure"),
    Output("entropy-value", "children"),
    Output("gini-value", "children"),
    Output("stddev-value", "children"),
    Output("best-fit-value", "children"),
    Output("js-uniform-value", "children"),
    Output("js-fv-value", "children"),
    Output("js-suliman-value", "children"),
    Output("metrics-history", "data"),
    Output("metrics-chart", "figure"),
    Output("results-table", "data"),
    Output("total-runs", "children"),
    Output("download-data", "data"),
    Output("best-fit-detail", "children"),
    Output("mode-display", "children"),
    Output("heatmap-data", "data"),  # Add this output
    Input("simulation-results", "data"),
    Input("model-checklist", "value"),
    Input("sort-checkbox", "value"),  # Add sort checkbox input
    Input("fraction-denominator", "data"),  # Add this input
    State("metrics-history", "data"),
    State("heatmap-data", "data"),  # Add this state
    prevent_initial_call=True,
)
def update_results(
    results, selected_models, sort_by, max_denominator, metrics_history, heatmap_data
):
    if not results:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
        empty_table = []
        return (
            empty_fig,
            "N/A",
            "N/A",
            "N/A",
            html.Div("N/A", className="text-center"),
            "N/A",
            "N/A",
            "N/A",
            metrics_history,
            empty_fig,
            empty_table,
            "0",
            {},
            "No simulation yet",
            "",
            heatmap_data,  # Return unchanged heatmap data
        )

    distribution = results.get("distribution", {})
    raw_counts = results.get("raw_counts", {})
    parameters = results.get("parameters", {})
    stats = results.get("stats", {})
    entropy_val = entropy(distribution)
    gini_val = gini(distribution)
    stddev = stats.get("stddev", 0)
    best_fit = stats.get("best_fit", "N/A")
    best_fit_js = stats.get("best_fit_js", 0)
    js_uniform = stats.get("js_uniform", 0)
    js_fv = stats.get("js_fv", 0)
    js_suliman = stats.get("js_suliman", 0)
    timestamp = stats.get("timestamp", "")
    run_count = len(metrics_history["runs"]) + 1
    metrics_history["runs"].append(run_count)
    metrics_history["entropy"].append(entropy_val)
    metrics_history["gini"].append(gini_val)
    metrics_history["stddev"].append(stddev)
    metrics_history["best_fit"].append(best_fit)
    metrics_history["js_uniform"].append(js_uniform)
    metrics_history["js_fv"].append(js_fv)
    metrics_history["js_suliman"].append(js_suliman)
    metrics_history["timestamps"].append(timestamp)
    metrics_history["params"].append(
        f"p={parameters.get('p_born', 0):.2f}, q={parameters.get('p_die', 0):.2f}"
    )
    relation_fig = go.Figure()
    allen_relations_list = list(ALLEN_RELATIONS)

    # Sort by frequency if requested
    if "sort" in sort_by:
        relation_value_pairs = [
            (rel, distribution.get(rel, 0)) for rel in allen_relations_list
        ]
        relation_value_pairs.sort(key=lambda x: x[1], reverse=True)
        allen_relations_list = [pair[0] for pair in relation_value_pairs]

    relation_names = [RELATION_NAMES.get(rel, rel) for rel in allen_relations_list]
    sim_values = [distribution.get(rel, 0) for rel in allen_relations_list]
    colors = [RELATION_COLORS.get(rel, "#000000") for rel in allen_relations_list]

    mode_relation = stats.get("mode", "")
    mode_name = stats.get("mode_name", "")
    mode_value = 0
    mode_color = ""

    if mode_relation in distribution:
        mode_value = distribution[mode_relation]
        mode_color = RELATION_COLORS.get(mode_relation, "#777777")

    mode_display = (
        html.Div(
            [
                html.Span("Mode: ", className="font-weight-bold"),
                html.Span(
                    mode_name,
                    style={
                        "color": mode_color,
                        "font-weight": "bold",
                        "padding": "0 4px",
                        "border-bottom": f"2px solid {mode_color}",
                    },
                ),
                html.Span(
                    f" ({format_number(mode_value, digits=3)})",
                    style={
                        "color": mode_color,
                    },
                ),
            ],
            style={"margin-top": "6px"},
        )
        if mode_relation
        else ""
    )

    relation_fig.add_trace(
        go.Bar(
            x=relation_names,
            y=sim_values,
            name="Simulation",
            marker_color=colors,
            text=sim_values,
            texttemplate="%{y:.3f}",
            textposition="outside",
            hovertemplate="%{x}: %{y:.4f}<extra></extra>",
        )
    )
    if "Uniform" in selected_models:
        relation_fig.add_trace(
            go.Scatter(
                x=relation_names,
                y=[UNIFORM_DISTRIBUTION.get(rel, 0) for rel in allen_relations_list],
                mode="lines+markers",
                name="Uniform",
                line=dict(color="black", width=2, dash="dash"),
                marker=dict(size=6, color="black"),
            )
        )
    if "Fernando-Vogel" in selected_models:
        relation_fig.add_trace(
            go.Scatter(
                x=relation_names,
                y=[
                    FERNANDO_VOGEL_DISTRIBUTION.get(rel, 0)
                    for rel in allen_relations_list
                ],
                mode="lines+markers",
                name="Fernando-Vogel",
                line=dict(color="black", width=2, dash="dot"),
                marker=dict(size=6, symbol="diamond", color="black"),
            )
        )
    if "Suliman" in selected_models:
        relation_fig.add_trace(
            go.Scatter(
                x=relation_names,
                y=[SULIMAN_DISTRIBUTION.get(rel, 0) for rel in allen_relations_list],
                mode="lines+markers",
                name="Suliman",
                line=dict(color="black", width=2, dash="dashdot"),
                marker=dict(size=6, symbol="square", color="black"),
            )
        )
    relation_fig.update_layout(
        title=f"Allen Relation Distribution (p={parameters.get('p_born', 0):.2f}, q={parameters.get('p_die', 0):.2f}, n={parameters.get('trials', 0)})",
        xaxis_title="Relation Type",
        yaxis_title="Probability",
        legend_title="Source",
        template="plotly_white",
        transition_duration=500,
        height=600,
        yaxis=dict(
            range=[0, max(max(sim_values) * 1.1, 0.2)],
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(
            tickangle=-45,
        ),
    )
    metrics_fig = make_subplots(specs=[[{"secondary_y": True}]])
    metrics_fig.add_trace(
        go.Scatter(
            x=metrics_history["runs"],
            y=metrics_history["entropy"],
            mode="lines+markers",
            name="Entropy",
            line=dict(color="blue", width=2),
        ),
        secondary_y=False,
    )
    metrics_fig.add_trace(
        go.Scatter(
            x=metrics_history["runs"],
            y=metrics_history["js_uniform"],
            mode="lines+markers",
            name="JS (Uniform)",
            line=dict(color="green", width=2, dash="dot"),
            marker=dict(size=6),
        ),
        secondary_y=False,
    )
    metrics_fig.add_trace(
        go.Scatter(
            x=metrics_history["runs"],
            y=metrics_history["js_fv"],
            mode="lines+markers",
            name="JS (F-V)",
            line=dict(color="purple", width=2, dash="dashdot"),
            marker=dict(size=6),
        ),
        secondary_y=False,
    )
    metrics_fig.add_trace(
        go.Scatter(
            x=metrics_history["runs"],
            y=metrics_history["js_suliman"],
            mode="lines+markers",
            name="JS (Suliman)",
            line=dict(color="orange", width=2, dash="dot"),
            marker=dict(size=6),
        ),
        secondary_y=False,
    )
    metrics_fig.add_trace(
        go.Scatter(
            x=metrics_history["runs"],
            y=metrics_history["gini"],
            mode="lines+markers",
            name="Gini Coefficient",
            line=dict(color="red", width=2),
        ),
        secondary_y=True,
    )
    hover_texts = []
    for i, params in enumerate(metrics_history["params"]):
        hover_texts.append(
            f"Run {i+1}<br>{params}<br>{metrics_history['timestamps'][i]}"
        )
    for trace in metrics_fig.data:
        trace.hovertext = hover_texts
        trace.hovertemplate = "%{hovertext}<br>%{y:.4f}<extra></extra>"
    metrics_fig.update_layout(
        title="Metrics Over Simulation Runs",
        xaxis_title="Run Number",
        template="plotly_white",
        transition_duration=500,
        hovermode="closest",
        height=400,
    )
    metrics_fig.update_yaxes(title_text="Entropy / JS Divergence", secondary_y=False)
    metrics_fig.update_yaxes(title_text="Gini Coefficient", secondary_y=True)
    table_data = []

    # Check if there are multiple non-zero probabilities
    show_fractions = sum(1 for v in distribution.values() if v > 0) > 1

    for rel in allen_relations_list:
        probability = distribution.get(rel, 0)
        fraction = (
            percentage_to_fraction(probability * 100, max_denominator)
            if probability > 0
            else "-"
        )

        table_data.append(
            {
                "relation": rel,
                "name": RELATION_NAMES.get(rel, "Unknown"),
                "count": raw_counts.get(rel, 0),
                "probability": format_number(probability),
                "fraction": fraction if show_fractions else "-",
            }
        )
    entropy_display = format_number(entropy_val)
    gini_display = format_number(gini_val)
    stddev_display = format_number(stddev)
    js_uniform_display = format_number(js_uniform)
    js_fv_display = format_number(js_fv)
    js_suliman_display = format_number(js_suliman)

    badge_color = (
        "success"
        if best_fit_js < 0.05
        else "warning" if best_fit_js < 0.15 else "danger"
    )

    best_fit_card = html.Div(
        [
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.Div(
                                [
                                    html.H4(
                                        best_fit,
                                        className="card-title mb-1 text-center",
                                    ),
                                    html.Div(
                                        [
                                            dbc.Badge(
                                                f"JS = {format_number(best_fit_js)}",
                                                color=badge_color,
                                                className="ml-1",
                                                id="best-fit-badge",
                                            ),
                                        ],
                                        className="text-center",
                                    ),
                                    dbc.Tooltip(
                                        "Lower JS = better theoretical match",
                                        target="best-fit-badge",
                                        placement="bottom",
                                    ),
                                ]
                            )
                        ],
                        className="py-2",
                    )
                ],
                className="border-0",
            )
        ],
        className="text-center",
    )

    js_color = "success"
    if best_fit_js > 0.1:
        js_color = "warning"
    if best_fit_js > 0.2:
        js_color = "danger"

    best_fit_content = html.Div(
        [
            html.Strong(f"Best Fit: {best_fit} "),
            html.Span(
                f"(JS = {format_number(best_fit_js)})", className=f"text-{js_color}"
            ),
            html.Hr(className="my-2"),
            html.Div(
                [
                    html.Span("Compared to: "),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Span("Uniform: "),
                                    html.Span(
                                        f"{format_number(js_uniform)}",
                                        className=f"text-{'success' if js_uniform < 0.1 else 'warning' if js_uniform < 0.2 else 'danger'}",
                                    ),
                                ]
                            ),
                            html.Li(
                                [
                                    html.Span("Fernando-Vogel: "),
                                    html.Span(
                                        f"{format_number(js_fv)}",
                                        className=f"text-{'success' if js_fv < 0.1 else 'warning' if js_fv < 0.2 else 'danger'}",
                                    ),
                                ]
                            ),
                            html.Li(
                                [
                                    html.Span("Suliman: "),
                                    html.Span(
                                        f"{format_number(js_suliman)}",
                                        className=f"text-{'success' if js_suliman < 0.1 else 'warning' if js_suliman < 0.2 else 'danger'}",
                                    ),
                                ]
                            ),
                        ],
                        className="mb-0 pl-3",
                    ),
                ]
            ),
        ]
    )

    download_data = {
        "parameters": parameters,
        "timestamp": timestamp,
        "metrics": {
            "entropy": entropy_val,
            "gini": gini_val,
            "stddev": stddev,
            "best_fit": best_fit,
            "js_uniform": js_uniform,
            "js_fv": js_fv,
            "js_suliman": js_suliman,
            "mode": mode_relation,
        },
        "distribution": distribution,
        "raw_counts": raw_counts,
    }

    # Update the heatmap data with this run's entropy value
    p_born = parameters.get("p_born", 0)
    p_die = parameters.get("p_die", 0)

    # Check if this (p,q) pair already exists in the heatmap data
    found = False
    for i in range(len(heatmap_data["p_values"])):
        if (
            abs(heatmap_data["p_values"][i] - p_born) < 1e-6
            and abs(heatmap_data["q_values"][i] - p_die) < 1e-6
        ):
            # Update existing data point (running average)
            count = heatmap_data["run_counts"][i]
            current_entropy = heatmap_data["entropy_values"][i]
            # Weighted average based on run count
            heatmap_data["entropy_values"][i] = (
                current_entropy * count + entropy_val
            ) / (count + 1)
            heatmap_data["run_counts"][i] += 1
            found = True
            break

    # If this is a new (p,q) pair, add it to the heatmap data
    if not found:
        heatmap_data["p_values"].append(p_born)
        heatmap_data["q_values"].append(p_die)
        heatmap_data["entropy_values"].append(entropy_val)
        heatmap_data["run_counts"].append(1)

    return (
        relation_fig,
        entropy_display,
        gini_display,
        stddev_display,
        best_fit_card,
        js_uniform_display,
        js_fv_display,
        js_suliman_display,
        metrics_history,
        metrics_fig,
        table_data,
        str(run_count),
        download_data,
        best_fit_content,
        mode_display,
        heatmap_data,  # Include updated heatmap data
    )


@app.callback(
    Output("relation-chart", "figure", allow_duplicate=True),
    Output("mode-display", "children", allow_duplicate=True),
    Input("model-checklist", "value"),
    Input("sort-checkbox", "value"),  # Add sort checkbox input
    State("simulation-results", "data"),
    prevent_initial_call=True,
)
def update_chart_models(selected_models, sort_by, results):
    if not results:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
        return empty_fig, ""

    distribution = results.get("distribution", {})
    parameters = results.get("parameters", {})
    stats = results.get("stats", {})

    mode_relation = stats.get("mode", "")
    mode_name = stats.get("mode_name", "")
    mode_value = 0
    mode_color = ""
    if mode_relation in distribution:
        mode_value = distribution[mode_relation]
        mode_color = RELATION_COLORS.get(mode_relation, "#777777")

    mode_display = (
        html.Div(
            [
                html.Span("Mode: ", className="font-weight-bold"),
                html.Span(
                    mode_name,
                    style={
                        "color": mode_color,
                        "font-weight": "bold",
                        "padding": "0 4px",
                        "border-bottom": f"2px solid {mode_color}",
                    },
                ),
                html.Span(
                    f" ({format_number(mode_value, digits=3)})",
                    style={
                        "color": mode_color,
                    },
                ),
            ],
            style={"margin-top": "6px"},
        )
        if mode_relation
        else ""
    )

    allen_relations_list = list(ALLEN_RELATIONS)

    # Sort by frequency if requested
    if "sort" in sort_by:
        relation_value_pairs = [
            (rel, distribution.get(rel, 0)) for rel in allen_relations_list
        ]
        relation_value_pairs.sort(key=lambda x: x[1], reverse=True)
        allen_relations_list = [pair[0] for pair in relation_value_pairs]

    relation_names = [RELATION_NAMES.get(rel, rel) for rel in allen_relations_list]
    sim_values = [distribution.get(rel, 0) for rel in allen_relations_list]
    colors = [RELATION_COLORS.get(rel, "#000000") for rel in allen_relations_list]

    relation_fig = go.Figure()

    relation_fig.add_trace(
        go.Bar(
            x=relation_names,
            y=sim_values,
            name="Simulation",
            marker_color=colors,
            text=sim_values,
            texttemplate="%{y:.3f}",
            textposition="outside",
            hovertemplate="%{x}: %{y:.4f}<extra></extra>",
        )
    )
    if "Uniform" in selected_models:
        relation_fig.add_trace(
            go.Scatter(
                x=relation_names,
                y=[UNIFORM_DISTRIBUTION.get(rel, 0) for rel in allen_relations_list],
                mode="lines+markers",
                name="Uniform",
                line=dict(color="black", width=2, dash="dash"),
                marker=dict(size=6, color="black"),
            )
        )
    if "Fernando-Vogel" in selected_models:
        relation_fig.add_trace(
            go.Scatter(
                x=relation_names,
                y=[
                    FERNANDO_VOGEL_DISTRIBUTION.get(rel, 0)
                    for rel in allen_relations_list
                ],
                mode="lines+markers",
                name="Fernando-Vogel",
                line=dict(color="black", width=2, dash="dot"),
                marker=dict(size=6, symbol="diamond", color="black"),
            )
        )
    if "Suliman" in selected_models:
        relation_fig.add_trace(
            go.Scatter(
                x=relation_names,
                y=[SULIMAN_DISTRIBUTION.get(rel, 0) for rel in allen_relations_list],
                mode="lines+markers",
                name="Suliman",
                line=dict(color="black", width=2, dash="dashdot"),
                marker=dict(size=6, symbol="square", color="black"),
            )
        )
    relation_fig.update_layout(
        title=f"Allen Relation Distribution (p={parameters.get('p_born', 0):.2f}, q={parameters.get('p_die', 0):.2f}, n={parameters.get('trials', 0)})",
        xaxis_title="Relation Type",
        yaxis_title="Probability",
        legend_title="Source",
        template="plotly_white",
        transition_duration=500,
        height=600,
        yaxis=dict(
            range=[0, max(max(sim_values) * 1.1, 0.2)],
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(
            tickangle=-45,
        ),
    )

    return relation_fig, mode_display


@app.callback(
    Output("download-png", "data"),
    Input("export-button", "n_clicks"),
    State("relation-chart", "figure"),
    prevent_initial_call=True,
)
def export_png(n_clicks, figure):
    """Export the current figure as a PNG file"""
    if not n_clicks or not figure:
        return dash.no_update

    try:
        # Create a timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"allen-relation-dist-{timestamp}.png"

        # Convert figure to a PNG image with high quality
        img_bytes = pio.to_image(figure, format="png", width=1200, height=800, scale=2)

        # Convert binary data to base64 string (required for Dash downloads)
        img_str = base64.b64encode(img_bytes).decode()

        # Return as downloadable content (correctly formatted for Dash)
        return dict(content=img_str, filename=filename, type="image/png", base64=True)
    except Exception as e:
        print(f"Error exporting PNG: {e}")
        return dash.no_update


@app.callback(
    Output("download-csv", "data"),
    Input("export-csv-button", "n_clicks"),
    State("download-data", "data"),
    prevent_initial_call=True,
)
def export_csv(n_clicks, data):
    if not n_clicks or not data:
        return dash.no_update
    distribution = data.get("distribution", {})
    parameters = data.get("parameters", {})
    df = pd.DataFrame(
        {
            "relation": list(distribution.keys()),
            "name": [RELATION_NAMES.get(rel, "Unknown") for rel in distribution.keys()],
            "probability": list(distribution.values()),
            "count": [
                data.get("raw_counts", {}).get(rel, 0) for rel in distribution.keys()
            ],
        }
    )
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    p_born = parameters.get("p_born", 0)
    p_die = parameters.get("p_die", 0)
    return dcc.send_data_frame(
        df.to_csv,
        f"allen-relations-p{p_born:.2f}-q{p_die:.2f}-{timestamp}.csv",
        index=False,
    )


@app.callback(
    Output("download-json", "data"),
    Input("export-json-button", "n_clicks"),
    State("download-data", "data"),
    prevent_initial_call=True,
)
def export_json(n_clicks, data):
    if not n_clicks or not data:
        return dash.no_update
    parameters = data.get("parameters", {})
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    p_born = parameters.get("p_born", 0)
    p_die = parameters.get("p_die", 0)
    return dict(
        content=json.dumps(data, indent=2),
        filename=f"allen-relations-p{p_born:.2f}-q{p_die:.2f}-{timestamp}.json",
        type="application/json",
    )


@app.callback(
    Output("loading-spinner", "children"),
    Input("run-button", "n_clicks"),
    prevent_initial_call=True,
)
def trigger_spinner(n_clicks):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    return dash.no_update


@app.callback(
    Output("history-summary", "children"),
    Input("metrics-history", "data"),
    prevent_initial_call=True,
)
def update_history_summary(history):
    if not history or not history.get("runs", []):
        return "No simulations run yet."
    run_count = len(history["runs"])
    if run_count > 0:
        last_params = history["params"][-1] if history["params"] else "N/A"
        return [
            html.P(f"Latest simulation: {last_params}", className="mb-1"),
            html.P(f"Best fit: {history['best_fit'][-1]}", className="mb-1"),
        ]
    return "No simulation data available."


@app.callback(
    Output("entropy-heatmap", "figure"),
    Input("heatmap-data", "data"),
    prevent_initial_call=True,
)
def update_entropy_heatmap(heatmap_data):
    # If no data or empty data, return an empty figure with instructions
    if not heatmap_data or not heatmap_data["p_values"]:
        fig = go.Figure()
        fig.update_layout(
            title="Entropy Heatmap",
            annotations=[
                {
                    "text": "Run simulations to populate the heatmap",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 14},
                }
            ],
            height=250,
            margin=dict(l=50, r=20, t=30, b=50),
        )
        return fig

    # Extract unique p and q values for the grid
    unique_p = sorted(list(set([round(p, 2) for p in heatmap_data["p_values"]])))
    unique_q = sorted(list(set([round(q, 2) for q in heatmap_data["q_values"]])))

    # Create the heatmap data structure
    heatmap_z = [[None for _ in range(len(unique_p))] for _ in range(len(unique_q))]
    run_counts_z = [[0 for _ in range(len(unique_p))] for _ in range(len(unique_q))]

    # Populate the grid
    for i in range(len(heatmap_data["p_values"])):
        p = heatmap_data["p_values"][i]
        q = heatmap_data["q_values"][i]
        entropy_val = heatmap_data["entropy_values"][i]
        runs = heatmap_data["run_counts"][i]

        # Find indices in the grid
        p_idx = unique_p.index(round(p, 2))
        q_idx = unique_q.index(round(q, 2))

        # Set the value
        heatmap_z[q_idx][p_idx] = entropy_val
        run_counts_z[q_idx][p_idx] = runs

    # Create the heatmap figure
    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_z,
            x=unique_p,
            y=unique_q,
            colorscale="Viridis",
            colorbar=dict(title="Entropy"),
            hovertemplate="p: %{x:.2f}<br>q: %{y:.2f}<br>Entropy: %{z:.4f}<extra></extra>",
            zmin=0,
            zmax=3.7,  # Max theoretical entropy for 13 relations
        )
    )

    # Add markers for run counts
    bubble_sizes = []
    bubble_x = []
    bubble_y = []
    hover_texts = []

    for q_idx, q in enumerate(unique_q):
        for p_idx, p in enumerate(unique_p):
            if run_counts_z[q_idx][p_idx] > 0:
                bubble_x.append(p)
                bubble_y.append(q)
                size = min(
                    run_counts_z[q_idx][p_idx] / 2, 10
                )  # Scale run count to reasonable size
                bubble_sizes.append(size)
                hover_texts.append(f"Runs: {run_counts_z[q_idx][p_idx]}")

    # Add scatter plot to show where simulations have been run
    fig.add_trace(
        go.Scatter(
            x=bubble_x,
            y=bubble_y,
            mode="markers",
            marker=dict(
                size=bubble_sizes,
                color="rgba(255, 255, 255, 0.7)",
                line=dict(color="rgba(0, 0, 0, 0.5)", width=1),
            ),
            hoverinfo="text",
            hovertext=hover_texts,
            showlegend=False,
        )
    )

    # Update layout
    fig.update_layout(
        title="Entropy Across Parameter Space",
        xaxis=dict(title="Birth Probability (p)"),
        yaxis=dict(title="Death Probability (q)"),
        height=250,
        margin=dict(l=50, r=20, t=30, b=50),
        transition_duration=500,  # Animation
    )

    return fig


@app.callback(
    Output("composition-results", "data"),
    Output("composition-spinner", "children", allow_duplicate=True),
    Input("run-composition-button", "n_clicks"),
    State("relation1-dropdown", "value"),
    State("relation2-dropdown", "value"),
    State("comp-p-born-input", "value"),  # Use input value instead of slider
    State("comp-p-die-input", "value"),  # Use input value instead of slider
    State("comp-trials-input", "value"),
    State("comp-limit-input", "value"),
    prevent_initial_call=True,
)
def run_composition(n_clicks, rel1, rel2, p_born, p_die, trials, limit):
    if n_clicks is None:
        return {}, dash.no_update

    # Validate inputs
    if (
        rel1 is None
        or rel2 is None
        or p_born is None
        or p_die is None
        or trials is None
        or limit is None
    ):
        error_card = dbc.Card(
            [
                dbc.CardHeader("Error"),
                dbc.CardBody(
                    [
                        html.H5("Invalid Input:"),
                        html.P("Please provide valid values for all parameters."),
                    ]
                ),
            ]
        )
        return {}, error_card

    # Generate valid triples with the given parameters
    try:
        triples = generate_valid_triples(p_born, p_die, trials, limit)

        # Build the composition table from the generated triples
        table = build_composition_table(triples)

        # Extract the specific composition we're looking for (rel1 ◦ rel2)
        composition = table.get(rel1, {}).get(rel2, {})

        # Calculate total count for this composition
        total_count = sum(composition.values())

        # Create a dictionary of results with percentages
        results = {
            "r1": rel1,
            "r2": rel2,
            "r1_name": RELATION_NAMES.get(rel1, "Unknown"),
            "r2_name": RELATION_NAMES.get(rel2, "Unknown"),
            "parameters": {
                "p_born": p_born,
                "p_die": p_die,
                "trials": trials,
                "limit": limit,
                "valid_count": len(triples),
            },
            "composition": {
                rel: {
                    "count": count,
                    "percentage": (count / total_count * 100) if total_count > 0 else 0,
                }
                for rel, count in composition.items()
            },
            "total_count": total_count,
        }

        return results, dash.no_update

    except Exception as e:
        # Handle errors
        error_card = dbc.Card(
            [
                dbc.CardHeader("Error"),
                dbc.CardBody(
                    [
                        html.H5("An error occurred during composition:"),
                        html.Pre(str(e), style={"color": "red"}),
                    ]
                ),
            ]
        )
        return {}, error_card


@app.callback(
    Output("composition-title", "children"),
    Output("composition-chart", "figure"),
    Output("composition-table", "data"),
    Output("comp-valid-count", "children"),
    Output("comp-most-common", "children"),
    Output("composition-summary", "children"),
    Input("composition-results", "data"),
    Input("comp-fraction-denominator", "data"),  # Add this input
    prevent_initial_call=True,
)
def update_composition_ui(results, max_denominator):
    if not results:
        # Return default values when no results are available
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="No composition data available",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            annotations=[
                {
                    "text": "Run a composition to see results",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16},
                }
            ],
        )
        return (
            "Select Relations and Run Composition",
            empty_fig,
            [],
            "0",
            "None",
            "No composition data available.",
        )

    # Extract data
    r1 = results.get("r1", "")
    r2 = results.get("r2", "")
    r1_name = results.get("r1_name", "")
    r2_name = results.get("r2_name", "")
    composition = results.get("composition", {})
    parameters = results.get("parameters", {})
    valid_count = parameters.get("valid_count", 0)
    total_count = results.get("total_count", 0)

    # Sort relations by percentage for the chart
    sorted_relations = sorted(
        [(rel, data) for rel, data in composition.items()],
        key=lambda x: x[1]["percentage"],
        reverse=True,
    )

    relation_codes = [rel for rel, _ in sorted_relations]
    relation_names = [RELATION_NAMES.get(rel, rel) for rel in relation_codes]
    percentages = [data["percentage"] for _, data in sorted_relations]
    counts = [data["count"] for _, data in sorted_relations]
    fractions = [percentage_to_fraction(pct, max_denominator) for pct in percentages]

    # Only show fractions in table if there are multiple outcomes
    show_fractions = len(sorted_relations) > 1

    # Set colors for the chart
    colors = [RELATION_COLORS.get(rel, "#000000") for rel in relation_codes]

    # Create the chart
    fig = go.Figure()

    # Fix: Use customdata for both counts and fractions instead of repeating text parameter
    custom_data = list(zip(counts, fractions))

    # Add horizontal bars instead of vertical ones - this works better for multiple relations
    fig.add_trace(
        go.Bar(
            y=relation_names,
            x=percentages,
            marker_color=colors,
            orientation="h",
            text=[f"{p:.2f}%" for p in percentages],
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>%{x:.2f}%<br>Count: %{customdata[0]}<br>≈ %{customdata[1]}<extra></extra>",
            customdata=custom_data,
        )
    )

    fig.update_layout(
        title=f"Composition: {r1} ({r1_name}) ◦ {r2} ({r2_name})",
        xaxis_title="Percentage (%)",
        yaxis_title="Resulting Relation (R3)",
        template="plotly_white",
        height=500,
        xaxis=dict(
            ticksuffix="%",
            range=[0, max(percentages) * 1.1] if percentages else [0, 100],
        ),
    )

    # Create data for the table
    table_data = [
        {
            "relation": rel,
            "name": RELATION_NAMES.get(rel, "Unknown"),
            "count": data["count"],
            "percentage": f"{data['percentage']:.2f}%",
            "fraction": fraction if show_fractions else "-",
        }
        for (rel, data), fraction in zip(sorted_relations, fractions)
    ]

    # Find the most common relation
    most_common_rel = ""
    most_common_pct = 0
    for rel, data in composition.items():
        if data["percentage"] > most_common_pct:
            most_common_rel = rel
            most_common_pct = data["percentage"]

    most_common_text = f"{most_common_rel} ({RELATION_NAMES.get(most_common_rel, 'Unknown')}) - {most_common_pct:.2f}%"

    # Create a more detailed summary
    p_born = parameters.get("p_born", 0)
    p_die = parameters.get("p_die", 0)
    trials = parameters.get("trials", 0)
    limit = parameters.get("limit", "No limit")
    outcome_count = len(sorted_relations)

    # Format as a table-like structure with bold labels
    summary = [
        html.Div(
            [
                html.Table(
                    [
                        html.Tr(
                            [
                                html.Td(
                                    html.Strong("Relation 1:"),
                                    style={
                                        "paddingRight": "10px",
                                        "textAlign": "right",
                                    },
                                ),
                                html.Td(f"{r1} ({r1_name})"),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td(
                                    html.Strong("Relation 2:"),
                                    style={
                                        "paddingRight": "10px",
                                        "textAlign": "right",
                                    },
                                ),
                                html.Td(f"{r2} ({r2_name})"),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td(
                                    html.Strong("Parameters:"),
                                    style={
                                        "paddingRight": "10px",
                                        "textAlign": "right",
                                    },
                                ),
                                html.Td(f"p={p_born}, q={p_die}"),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td(
                                    html.Strong("Trials:"),
                                    style={
                                        "paddingRight": "10px",
                                        "textAlign": "right",
                                    },
                                ),
                                html.Td(f"{trials} (limit: {limit})"),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td(
                                    html.Strong("Sample Size:"),
                                    style={
                                        "paddingRight": "10px",
                                        "textAlign": "right",
                                    },
                                ),
                                html.Td(f"{total_count} compositions found"),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td(
                                    html.Strong("Outcomes:"),
                                    style={
                                        "paddingRight": "10px",
                                        "textAlign": "right",
                                    },
                                ),
                                html.Td(f"{outcome_count} possible relation(s)"),
                            ]
                        ),
                    ],
                    style={"marginBottom": "10px"},
                )
            ]
        )
    ]

    # Update the composition table columns to include fractions
    columns = [
        {"name": "Relation", "id": "relation"},
        {"name": "Name", "id": "name"},
        {"name": "Count", "id": "count"},
        {"name": "Percentage", "id": "percentage"},
    ]

    if show_fractions:
        columns.append({"name": "≈ Fraction", "id": "fraction"})

    # Return all values
    return (
        f"Composition: {r1} ({r1_name}) ◦ {r2} ({r2_name})",
        fig,
        table_data,
        str(valid_count),
        most_common_text,
        summary,
    )


@app.callback(
    Output("matrix-results", "data"),
    Output("matrix-spinner", "children"),
    Output("matrix-status", "children"),
    Output(
        "matrix-global-stats", "children", allow_duplicate=True
    ),  # Fix callback conflict
    Input("run-matrix-button", "n_clicks"),
    State("matrix-p-born-input", "value"),
    State("matrix-p-die-input", "value"),
    State("matrix-trials-input", "value"),
    State("matrix-limit-input", "value"),
    prevent_initial_call=True,
)
def run_matrix_calculation(n_clicks, p_born, p_die, trials, limit):
    if n_clicks is None:
        return None, dash.no_update, dash.no_update, dash.no_update

    # Add validation for input values
    if p_born is None or p_die is None or trials is None or limit is None:
        error_status = dbc.Alert(
            "Error: Please provide valid values for all parameters.",
            color="danger",
        )
        return None, dash.no_update, error_status, dash.no_update

    try:
        # Calculate the matrix - this may take some time
        start_time = datetime.now()
        matrix_data, valid_count, global_stats = generate_full_composition_matrix(
            p_born, p_die, trials, limit
        )
        end_time = datetime.now()
        calculation_duration = end_time - start_time

        # Count coverage - how many cells have data vs total possible combinations
        total_cells = len(ALLEN_RELATIONS) * len(ALLEN_RELATIONS)
        populated_cells = 0

        # Track missing compositions for detailed reporting
        missing_compositions = []

        for r1 in ALLEN_RELATIONS:
            if r1 in matrix_data:
                for r2 in ALLEN_RELATIONS:
                    if r2 in matrix_data[r1]:
                        populated_cells += 1
                    else:
                        missing_compositions.append(f"{r1} ∘ {r2}")
            else:
                missing_compositions.extend([f"{r1} ∘ {r2}"] for r2 in ALLEN_RELATIONS)

        # Create a result object with metadata
        result = {
            "parameters": {
                "p_born": p_born,
                "p_die": p_die,
                "trials": trials,
                "limit_per_cell": limit,
                "valid_count": valid_count,
                "coverage": f"{populated_cells} / {total_cells}",
                "missing_count": len(missing_compositions),
                "missing_compositions": missing_compositions,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "duration": str(calculation_duration).split(".")[0],
            },
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "matrix": matrix_data,
            "global_stats": global_stats,
        }

        # Create missing compositions dropdown content
        missing_details = None
        if missing_compositions:
            missing_details = html.Details(
                [
                    html.Summary(f"Missing compositions: {len(missing_compositions)}"),
                    html.Ul(
                        [html.Li(comp) for comp in missing_compositions[:20]],
                        className="mb-0",
                    ),
                    html.Small(
                        f"(+{len(missing_compositions) - 20} more)"
                        if len(missing_compositions) > 20
                        else ""
                    ),
                ],
                className="mt-2",
            )

        # Create spinner children with all three visualizations
        matrix_spinner_children = [
            dbc.Card(
                [
                    dbc.CardHeader(
                        html.H5(
                            [
                                "Allen Relation Composition Matrix ",
                                html.Small(
                                    f"(p={p_born}, q={p_die}, n={trials})",
                                    className="text-muted",
                                ),
                            ],
                            className="mb-0",
                            id="matrix-title",
                        )
                    ),
                    dbc.CardBody(
                        [
                            html.P(
                                "The matrix shows the composition of Allen relations R1 (rows) with R2 (columns).",
                                className="text-muted",
                            ),
                            html.P(
                                [
                                    "Hover over cells to see detailed composition results.",
                                ],
                                className="text-muted small",
                            ),
                            html.Div(
                                dcc.Loading(
                                    id="loading-matrix",
                                    type="default",
                                    children=dcc.Graph(
                                        id="matrix-heatmap",
                                        config={"responsive": True},
                                        style={"height": "700px"},
                                    ),
                                ),
                            ),
                            html.Div(id="cell-details", className="mt-3"),
                        ]
                    ),
                ]
            ),
            dbc.Card(
                [
                    dbc.CardHeader("Entropy Heatmap of Composition Outcomes"),
                    dbc.CardBody(
                        [
                            html.P(
                                "This heatmap shows the entropy (uncertainty) of R3 outcomes for each composition pair.",
                                className="text-muted",
                            ),
                            dcc.Graph(
                                id="entropy-composition-heatmap",
                                config={"responsive": True},
                                style={"height": "500px"},
                            ),
                        ]
                    ),
                ],
                className="mt-4",
            ),
            dbc.Card(
                [
                    dbc.CardHeader("Global R3 Distribution"),
                    dbc.CardBody(
                        [
                            html.P(
                                "This chart shows the overall probability of each Allen relation appearing as an R3 outcome across all compositions.",
                                className="text-muted",
                            ),
                            dcc.Graph(
                                id="global-r3-distribution",
                                config={"responsive": True},
                                style={"height": "400px"},
                            ),
                        ]
                    ),
                ],
                className="mt-4",
            ),
            html.Div(
                [
                    html.Hr(className="mt-4"),
                    get_reference_tables(),
                ],
                className="mt-4",
                style={"width": "100%"},
            ),
        ]

        # Create enhanced status alert with summary information
        status = dbc.Alert(
            [
                html.H6("Matrix calculated successfully", className="alert-heading"),
                html.Div(
                    [
                        html.P(
                            [
                                html.Strong("Generated: "),
                                f"{result['parameters']['timestamp']}",
                            ],
                            className="mb-1",
                        ),
                        html.P(
                            [
                                html.Strong("Duration: "),
                                f"{result['parameters']['duration']}",
                            ],
                            className="mb-1",
                        ),
                        html.P(
                            [html.Strong("Trials: "), f"{trials:,}"], className="mb-1"
                        ),
                        html.P(
                            [html.Strong("Valid Runs: "), f"{valid_count:,}"],
                            className="mb-1",
                        ),
                        html.P(
                            [
                                html.Strong("Coverage: "),
                                f"{populated_cells} / {total_cells}",
                            ],
                            className="mb-1",
                        ),
                        html.P(
                            [html.Strong("Birth Probability (p): "), f"{p_born}"],
                            className="mb-1",
                        ),
                        html.P(
                            [html.Strong("Death Probability (q): "), f"{p_die}"],
                            className="mb-1",
                        ),
                    ]
                ),
                missing_details if missing_compositions else "",
            ],
            color="success",
            className="mt-3",
        )

        # Get global stats display
        global_stats_html = update_matrix_global_stats(data=result)

        return result, matrix_spinner_children, status, global_stats_html

    except Exception as e:
        # Handle errors
        error_card = [
            dbc.Card(
                [
                    dbc.CardHeader("Error"),
                    dbc.CardBody(
                        [
                            html.H5("An error occurred during calculation:"),
                            html.Pre(str(e), style={"color": "red"}),
                        ]
                    ),
                ]
            ),
            html.Div(
                [
                    html.Hr(className="mt-4"),
                    get_reference_tables(),
                ],
                className="mt-4",
                style={"width": "100%"},
            ),
        ]

        error_status = dbc.Alert(
            f"Error: {str(e)}",
            color="danger",
        )

        return None, error_card, error_status, dash.no_update


@app.callback(
    Output("matrix-heatmap", "figure"),
    Input("matrix-results", "data"),
    prevent_initial_call=True,
)
def update_matrix_visualization(data):
    if not data or not data.get("matrix"):
        # Create an empty figure with a message
        fig = go.Figure()
        fig.update_layout(
            title="No matrix data available yet",
            annotations=[
                {
                    "text": "Click 'Calculate Matrix' to generate the visualization",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 16},
                }
            ],
        )
        return fig

    # Extract matrix data
    matrix = data.get("matrix", {})
    params = data.get("parameters", {})

    # Create a 13×13 matrix for visualization following Alspaugh's convention
    x = list(ALLEN_RELATIONS)  # Columns (R2)
    y = list(
        reversed(ALLEN_RELATIONS)
    )  # Rows (R1) - reversed to match traditional order

    # Alspaugh's background colors for cells
    alspaugh_colors = {
        "p": "#eef",
        "P": "#ccf",
        "d": "#fee",
        "D": "#fcc",
        "osd": "#efe",
        "DSO": "#cfc",
        "oFD": "#ddf",
        "dfO": "#bbf",
        "m": "#fdd",
        "M": "#fbb",
        "pmosd": "#dfd",
        "DSOMP": "#bfb",
        "pmoFD": "#ffb",
        "dfOMP": "#ff8",
        "o": "#fbf",
        "O": "#f8f",
        "pmo": "#bff",
        "OMP": "#8ff",
        "s": "#edb",
        "S": "#eb9",
        "f": "#deb",
        "F": "#be9",
        "seS": "#bed",
        "Fef": "#9eb",
        "e": "#d9c",
        "concur": "#bde",
        "full": "#9be",
    }

    # Create figure with custom layout
    fig = go.Figure()

    # Define special relation sets precisely (exact strings for consistent comparison)
    full_relations_set = set(ALLEN_RELATIONS)  # All 13 relations: pmoFDseSdfOMP
    concur_relations_set = set("oFDseSdfO")  # The 9 concurrent relations

    # Create hover text for each cell and determine cell styling
    annotations = []

    for i, r1 in enumerate(y):  # For each row (R1)
        for j, r2 in enumerate(x):  # For each column (R2)
            cell_data = matrix.get(r1, {}).get(r2, {"composition": {}, "total": 0})
            composition = cell_data.get("composition", {})
            total = cell_data.get("total", 0)

            if total == 0:
                # No data for this cell
                continue

            # Generate hover text with all relations and percentages
            hover_parts = [
                f"R1: {r1} ({RELATION_NAMES.get(r1, 'Unknown')})<br>R2: {r2} ({RELATION_NAMES.get(r2, 'Unknown')})"
            ]

            # Sort relations by Allen order for consistent display in hover
            for rel in ALLEN_RELATIONS:
                if rel in composition:
                    data = composition[rel]
                    pct = data["percentage"]
                    count = data["count"]
                    hover_parts.append(
                        f"{rel} ({RELATION_NAMES.get(rel, 'Unknown')}): {pct:.1f}% ({count})"
                    )

            hover_text = "<br>".join(hover_parts)

            # Get list of all relations present in the composition (even with very small percentages)
            # This ensures consistent detection of full and concur patterns
            present_rels = set(composition.keys())

            cell_text = ""
            cell_color = "#ffffff"
            font_style = "normal"

            # Check for special cases consistently - exact set matching
            # Full relation set - all 13 Allen relations
            if present_rels == full_relations_set or "".join(
                sorted(present_rels)
            ) == "".join(sorted(ALLEN_RELATIONS)):
                cell_text = "full"
                cell_color = alspaugh_colors["full"]
                font_style = "italic"
            # Concurrent relation set - exact match with the 9 concurrent relations
            elif present_rels == concur_relations_set or "".join(
                sorted(present_rels)
            ) == "".join(sorted("oFDseSdfO")):
                cell_text = "concur"
                cell_color = alspaugh_colors["concur"]
                font_style = "italic"
            # Also check if we have a parenthetical notation that matches these special cases
            elif "".join(sorted(present_rels)) == "".join(sorted(ALLEN_RELATIONS)):
                cell_text = "full"  # Force "full" for any cell with all relations
                cell_color = alspaugh_colors["full"]
                font_style = "italic"
            elif "".join(sorted(present_rels)) == "".join(sorted("oFDseSdfO")):
                cell_text = "concur"  # Force "concur" for any cell with exactly concurrent relations
                cell_color = alspaugh_colors["concur"]
                font_style = "italic"
            else:
                # Consider only relations with >1% probability for regular cases
                significant_rels = set(
                    rel for rel, data in composition.items() if data["percentage"] > 1
                )

                # Find dominant relation if one exists (>80%)
                sorted_rels = sorted(
                    [(rel, data) for rel, data in composition.items()],
                    key=lambda x: x[1]["percentage"],
                    reverse=True,
                )

                dominant_rel = sorted_rels[0][0] if sorted_rels else ""
                dominant_pct = sorted_rels[0][1]["percentage"] if sorted_rels else 0

                if dominant_pct > 80:
                    # Single dominant relation
                    cell_text = dominant_rel
                    cell_color = alspaugh_colors.get(dominant_rel, "#ffffff")
                elif len(significant_rels) <= 5:
                    # Small set of relations - show them all in Allen order
                    sorted_rels = [
                        rel for rel in ALLEN_RELATIONS if rel in significant_rels
                    ]
                    cell_text = "".join(sorted_rels)
                    # Try to find matching color in Alspaugh's scheme
                    cell_color = alspaugh_colors.get(cell_text, "#f5f5f5")
                else:
                    # Many relations - use abbreviated notation
                    sorted_rels = [
                        rel for rel in ALLEN_RELATIONS if rel in significant_rels
                    ]
                    cell_text = "(" + "".join(sorted_rels) + ")"
                    cell_color = "#f0f0f0"

            # Add cell with proper background
            fig.add_shape(
                type="rect",
                x0=j - 0.5,
                y0=i - 0.5,
                x1=j + 0.5,
                y1=i + 0.5,
                line=dict(color="#eeeeee", width=0.5),  # Very light gray lines
                fillcolor=cell_color,
                layer="below",
            )

            # Add text annotation with black text
            if cell_text:
                annotations.append(
                    dict(
                        x=j,
                        y=i,
                        text=cell_text,
                        showarrow=False,
                        font=dict(
                            color="#000000",  # Black text for all cells
                            size=12 if len(cell_text) < 10 else 10,
                            family="sans-serif",
                        ),
                        hovertext=hover_text,
                        hoverlabel=dict(
                            bgcolor="white", font_size=12, font_family="Arial"
                        ),
                    )
                )

    # Configure axes
    fig.update_xaxes(
        tickmode="array",
        tickvals=list(range(len(x))),
        ticktext=x,
        title="R2 (Second Relation)",
        side="bottom",
        tickfont=dict(size=12),
    )

    fig.update_yaxes(
        tickmode="array",
        tickvals=list(range(len(y))),
        ticktext=y,
        title="R1 (First Relation)",
        tickfont=dict(size=12),
    )

    # Add the annotations
    fig.update_layout(
        annotations=annotations,
        title=f"Allen Relation Composition Matrix (p={params.get('p_born', 0):.2f}, q={params.get('p_die', 0):.2f})",
        height=700,
        plot_bgcolor="white",
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        xaxis=dict(range=[-0.5, len(x) - 0.5]),
        yaxis=dict(range=[-0.5, len(y) - 0.5]),
        transition_duration=500,  # Animation
    )

    return fig


@app.callback(
    Output("cell-details", "children"),
    Input("matrix-heatmap", "clickData"),
    Input("matrix-fraction-denominator", "data"),
    State("matrix-results", "data"),
    prevent_initial_call=True,
)
def display_cell_details(click_data, max_denominator, matrix_results):
    if not click_data or not matrix_results:
        return ""

    # Extract clicked cell information
    points = click_data.get("points", [{}])[0]
    x_val = points.get("x")  # R2
    y_val = points.get("y")  # R1

    if not x_val or not y_val:
        return ""

    # Get the cell data
    matrix = matrix_results.get("matrix", {})
    cell_data = matrix.get(y_val, {}).get(x_val, {"composition": {}, "total": 0})
    composition = cell_data.get("composition", {})
    total = cell_data.get("total", 0)

    if total == 0:
        return html.P(f"No composition data available for {y_val} ◦ {x_val}")

    # Sort relations by percentage
    sorted_rels = sorted(
        [(rel, data) for rel, data in composition.items()],
        key=lambda x: x[1]["percentage"],
        reverse=True,
    )

    # Calculate metrics
    composition_dist = {
        rel: data["percentage"] / 100 for rel, data in composition.items()
    }
    entropy_val = entropy(composition_dist)

    # Create a Bar chart for the composition
    rels = [rel for rel, _ in sorted_rels]
    pcts = [data["percentage"] for _, data in sorted_rels]
    counts = [data["count"] for _, data in sorted_rels]
    colors = [RELATION_COLORS.get(rel, "#000000") for rel in rels]

    fig = go.Figure(
        data=[
            go.Bar(
                x=rels,
                y=pcts,
                marker_color=colors,
                text=[f"{p:.2f}%" for p in pcts],
                textposition="outside",
                hovertemplate="%{x}: %{y:.2f}%<br>Count: %{customdata}<extra></extra>",
                customdata=counts,
            )
        ]
    )

    fig.update_layout(
        title=f"Composition: {y_val} ({RELATION_NAMES.get(y_val, '')}) ◦ {x_val} ({RELATION_NAMES.get(x_val, '')})",
        xaxis_title="Resulting Relation (R3)",
        yaxis_title="Percentage (%)",
        yaxis=dict(
            range=[0, max(pcts) * 1.1] if pcts else [0, 100],
        ),
        height=300,
        margin=dict(t=50, b=50),
    )

    # Create a table with detailed results
    table_data = []
    for rel, data in sorted_rels:
        pct = data["percentage"]
        count = data["count"]
        fraction = percentage_to_fraction(pct, max_denominator)

        table_data.append(
            {
                "relation": rel,
                "name": RELATION_NAMES.get(rel, "Unknown"),
                "count": count,
                "percentage": f"{pct:.2f}%",
                "fraction": fraction,
            }
        )

    # Return the detailed view
    return html.Div(
        [
            html.H5(f"Composition Details: {y_val} ◦ {x_val}"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong("Total samples:"),
                            f" {total}",
                            html.Br(),
                            html.Strong("Entropy:"),
                            f" {entropy_val:.4f}",
                        ],
                        className="mb-3",
                    ),
                    dcc.Graph(figure=fig, config={"displayModeBar": False}),
                    dash_table.DataTable(
                        data=table_data,
                        columns=[
                            {"name": "Relation", "id": "relation"},
                            {"name": "Name", "id": "name"},
                            {"name": "Count", "id": "count"},
                            {"name": "Percentage", "id": "percentage"},
                            {"name": "≈ Fraction", "id": "fraction"},
                        ],
                        style_table={"overflowX": "auto"},
                        style_cell={"textAlign": "left", "padding": "8px"},
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                        },
                    ),
                ]
            ),
        ]
    )


@app.callback(
    Output("single-composition-container", "style", allow_duplicate=True),
    Output("matrix-composition-container", "style", allow_duplicate=True),
    Output("valid-relations-container", "style"),
    Output("most-common-container", "style"),
    Input("composition-mode-tabs", "active_tab"),
    prevent_initial_call=True,
)
def toggle_composition_view(active_tab):
    if active_tab == "tab-single-comp":
        # Show single composition, hide matrix, show stats
        return (
            {"display": "block"},
            {"display": "none"},
            {"display": "block"},
            {"display": "block"},
        )
    else:  # tab-full-matrix
        # Hide single composition, show matrix, hide stats
        return (
            {"display": "none"},
            {"display": "block"},
            {"display": "none"},
            {"display": "none"},
        )


@app.callback(
    Output("matrix-global-stats", "children"),
    Input("matrix-results", "data"),
    prevent_initial_call=True,
)
def update_matrix_global_stats(data):
    if not data or not data.get("global_stats"):
        return html.Div("No global statistics available yet")

    # Extract global statistics
    global_stats = data["global_stats"]
    distribution = global_stats.get("distribution", {})
    entropy_val = global_stats.get("entropy", 0)
    gini_val = global_stats.get("gini", 0)
    js_uniform = global_stats.get("js_uniform", 0)
    js_fv = global_stats.get("js_fv", 0)
    js_suliman = global_stats.get("js_suliman", 0)
    best_fit = global_stats.get("best_fit", "N/A")
    best_fit_js = global_stats.get("best_fit_js", 0)
    mode_relation = global_stats.get("mode", "N/A")
    mode_name = global_stats.get("mode_name", "N/A")

    # Determine colors for JS divergence values based on how good the fit is
    js_uniform_color = (
        "success" if js_uniform < 0.1 else "warning" if js_uniform < 0.2 else "danger"
    )
    js_fv_color = "success" if js_fv < 0.1 else "warning" if js_fv < 0.2 else "danger"
    js_suliman_color = (
        "success" if js_suliman < 0.1 else "warning" if js_suliman < 0.2 else "danger"
    )
    best_fit_color = (
        "success" if best_fit_js < 0.1 else "warning" if best_fit_js < 0.2 else "danger"
    )

    return html.Div(
        [
            html.Div(
                [
                    html.Strong("Global R3 Distribution Statistics"),
                    html.Br(),
                    html.Small(
                        "(Aggregated across all 169 R1•R2 composition pairs)",
                        className="text-muted",
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Strong("Entropy: "),
                            html.Span(f"{entropy_val:.4f}"),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.Strong("Gini Coefficient: "),
                            html.Span(f"{gini_val:.4f}"),
                        ],
                        md=6,
                    ),
                ],
                className="mb-2",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Strong("JS (Uniform): "),
                            html.Span(
                                f"{js_uniform:.4f}",
                                className=f"text-{js_uniform_color}",
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            html.Strong("JS (F-V): "),
                            html.Span(f"{js_fv:.4f}", className=f"text-{js_fv_color}"),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            html.Strong("JS (Suliman): "),
                            html.Span(
                                f"{js_suliman:.4f}",
                                className=f"text-{js_suliman_color}",
                            ),
                        ],
                        md=4,
                    ),
                ],
                className="mb-2",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Strong("Best Fit Model: "),
                            html.Span(
                                f"{best_fit} (JS = {best_fit_js:.4f})",
                                className=f"text-{best_fit_color}",
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.Strong("Most Common R3: "),
                            html.Span(f"{mode_relation} - {mode_name}"),
                        ],
                        md=6,
                    ),
                ],
                className="mb-2",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button(
                                "Export Global Distribution",
                                id="export-global-dist-button",
                                color="secondary",
                                size="sm",
                                className="mt-3",
                            ),
                            dbc.Tooltip(
                                "Download the global R3 distribution as CSV",
                                target="export-global-dist-button",
                                placement="top",
                            ),
                        ],
                        width={"size": 6, "offset": 3},
                        className="text-center",
                    ),
                ]
            ),
        ]
    )


# Add export functionality for global distribution data
@app.callback(
    Output("download-global-dist", "data"),
    Input("export-global-dist-button", "n_clicks"),
    State("matrix-results", "data"),
    prevent_initial_call=True,
)
def export_global_distribution(n_clicks, data):
    if not n_clicks or not data or not data.get("global_stats"):
        return dash.no_update

    global_stats = data["global_stats"]
    distribution = global_stats.get("distribution", {})
    raw_counts = global_stats.get("raw_counts", {})
    parameters = data.get("parameters", {})

    # Create a dataframe with the sorted distribution data
    sorted_relations = sorted(distribution.items(), key=lambda x: x[1], reverse=True)

    df = pd.DataFrame(
        {
            "relation": [rel for rel, _ in sorted_relations],
            "name": [RELATION_NAMES.get(rel, "Unknown") for rel, _ in sorted_relations],
            "probability": [prob for _, prob in sorted_relations],
            "count": [raw_counts.get(rel, 0) for rel, _ in sorted_relations],
        }
    )

    # Generate a filename with parameters
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    p_born = parameters.get("p_born", 0)
    p_die = parameters.get("p_die", 0)

    return dcc.send_data_frame(
        df.to_csv,
        f"allen-global-dist-p{p_born:.2f}-q{p_die:.2f}-{timestamp}.csv",
        index=False,
    )


@app.callback(
    Output("entropy-composition-heatmap", "figure"),
    Input("matrix-results", "data"),
    prevent_initial_call=True,
)
def update_entropy_heatmap(data):
    if not data or not data.get("matrix"):
        # Return empty figure with instructions if no data
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="Entropy Heatmap - No Data",
            annotations=[
                {
                    "text": "Run matrix calculation to populate the entropy heatmap",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 14},
                }
            ],
            height=500,
            margin=dict(l=50, r=20, t=50, b=50),
        )
        return empty_fig

    # Extract matrix data
    matrix = data.get("matrix", {})
    params = data.get("parameters", {})

    # Create arrays for the heatmap
    x = list(ALLEN_RELATIONS)  # Columns (R2)
    y = list(
        reversed(ALLEN_RELATIONS)
    )  # Rows (R1) - reversed to match traditional visualization

    # Initialize the z-values (entropy) and hover text matrices
    z = []
    hover_text = []

    for r1 in y:
        entropy_row = []
        hover_row = []
        for r2 in x:
            cell_data = matrix.get(r1, {}).get(r2, {"composition": {}, "total": 0})
            composition = cell_data.get("composition", {})
            total = cell_data.get("total", 0)

            # Calculate entropy if we have data
            if total > 0:
                distribution = {
                    rel: data["percentage"] / 100 for rel, data in composition.items()
                }
                entropy_val = entropy(distribution)

                # Find most probable outcome
                most_probable = None
                max_prob = 0
                for rel, data in composition.items():
                    if data["percentage"] > max_prob:
                        most_probable = rel
                        max_prob = data["percentage"]

                # Format hover text with detailed information
                hover_info = (
                    f"R1: {r1} ({RELATION_NAMES.get(r1, 'Unknown')})<br>"
                    + f"R2: {r2} ({RELATION_NAMES.get(r2, 'Unknown')})<br>"
                    + f"Entropy: {entropy_val:.4f}<br>"
                    + f"Most probable: {most_probable} ({RELATION_NAMES.get(most_probable, 'Unknown')})<br>"
                    + f"Probability: {max_prob:.2f}%"
                )
            else:
                entropy_val = None
                hover_info = (
                    f"R1: {r1} ({RELATION_NAMES.get(r1, 'Unknown')})<br>"
                    + f"R2: {r2} ({RELATION_NAMES.get(r2, 'Unknown')})<br>"
                    + "No data"
                )

            entropy_row.append(entropy_val)
            hover_row.append(hover_info)

        z.append(entropy_row)
        hover_text.append(hover_row)

    # Create the heatmap figure
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=x,
            y=y,
            colorscale="Viridis",
            colorbar=dict(
                title=dict(  # Fix: changed from titleside to proper nested title structure
                    text="Entropy", side="right", font=dict(size=14)
                ),
            ),
            hoverinfo="text",
            text=hover_text,
            zmin=0,
            zmax=3.7,  # Max theoretical entropy for 13 relations is log(13) ≈ 3.7
        )
    )

    # Update layout with nice formatting
    fig.update_layout(
        title={
            "text": f"Entropy of R3 Outcomes for Each Composition Pair (p={params.get('p_born', 0):.2f}, q={params.get('p_die', 0):.2f})",
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title="R2 (Second Relation)",
        yaxis_title="R1 (First Relation)",
        height=500,
        margin=dict(l=50, r=20, t=50, b=50),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(x))),
            ticktext=x,
            title_standoff=15,
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(len(y))),
            ticktext=y,
            title_standoff=15,
        ),
        annotations=[
            dict(
                text="Darker = More Uncertain",
                x=1.01,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=12),
                textangle=-90,
            )
        ],
    )

    return fig


# Add missing callback for global R3 distribution chart
@app.callback(
    Output("global-r3-distribution", "figure"),
    Input("matrix-results", "data"),
    prevent_initial_call=True,
)
def update_global_r3_distribution(data):
    if not data or not data.get("global_stats"):
        # Return empty figure with instructions if no data
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="Global R3 Distribution - No Data",
            annotations=[
                {
                    "text": "Run matrix calculation to see the global distribution",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 14},
                }
            ],
            height=400,
            margin=dict(l=50, r=20, t=50, b=50),
        )
        return empty_fig

    # Extract global statistics
    global_stats = data.get("global_stats", {})
    distribution = global_stats.get("distribution", {})
    raw_counts = global_stats.get("raw_counts", {})
    params = data.get("parameters", {})

    if not distribution:
        return empty_fig

    # Use standard ALLEN_RELATIONS order instead of sorting by frequency
    relation_codes = list(ALLEN_RELATIONS)
    relation_names = [RELATION_NAMES.get(rel, rel) for rel in relation_codes]
    probabilities = [distribution.get(rel, 0) * 100 for rel in relation_codes]
    counts = [raw_counts.get(rel, 0) for rel in relation_codes]
    colors = [RELATION_COLORS.get(rel, "#000000") for rel in relation_codes]

    # Create the bar chart
    fig = go.Figure()

    # Use customdata for hover information
    custom_data = list(zip(counts, [f"{p:.2f}%" for p in probabilities]))

    fig.add_trace(
        go.Bar(
            x=relation_codes,
            y=probabilities,
            marker_color=colors,
            text=[f"{p:.2f}%" for p in probabilities],
            textposition="outside",
            hovertemplate="<b>%{x}</b> - %{customdata[1]}<br>Count: %{customdata[0]}<br>%{text}<extra></extra>",
            customdata=custom_data,
        )
    )

    # Add theoretical models reference lines if needed
    # For example:
    # fig.add_trace(
    #     go.Scatter(
    #         x=relation_codes,
    #         y=[UNIFORM_DISTRIBUTION.get(rel, 0) * 100 for rel in relation_codes],
    #         mode="lines+markers",
    #         name="Uniform",
    #         line=dict(color="black", width=2, dash="dash"),
    #     )
    # )

    fig.update_layout(
        title=f"Global R3 Distribution (p={params.get('p_born', 0):.2f}, q={params.get('p_die', 0):.2f})",
        xaxis_title="Relation Type (R3)",
        yaxis_title="Probability (%)",
        template="plotly_white",
        height=400,
        xaxis=dict(
            tickangle=-45,
            tickmode="array",
            tickvals=relation_codes,
            ticktext=[
                f"{code} - {name}" for code, name in zip(relation_codes, relation_names)
            ],
        ),
        yaxis=dict(
            ticksuffix="%",
            range=[0, max(probabilities) * 1.1] if probabilities else [0, 100],
        ),
    )

    return fig


@app.callback(
    Output("simulation-results", "data", allow_duplicate=True),
    Output("upload-json-status", "children"),
    Output("p-born-input", "value", allow_duplicate=True),
    Output("p-die-input", "value", allow_duplicate=True),
    Output("trials-input", "value", allow_duplicate=True),
    Input("upload-json", "contents"),
    State("upload-json", "filename"),
    prevent_initial_call=True,
)
def process_uploaded_json(contents, filename):
    """Process uploaded JSON file and update app state for simulation tab"""
    if contents is None:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    try:
        # Decode the base64 encoded file contents
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        data = json.loads(decoded.decode("utf-8"))

        # Check if this is a simulation file
        is_sim_file = filename.startswith("sim_") or "results" in data

        if not is_sim_file:
            return (
                dash.no_update,
                dbc.Alert(
                    f"File format not recognized as simulation data: {filename}. Expected filename format: sim_p[value]_q[value].json",
                    color="warning",
                    dismissable=True,
                    duration=4000,
                ),
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )

        # Extract parameters from filename or metadata
        p_born = 0.5
        p_die = 0.5
        trials = 100000

        # Try to extract from filename
        match = re.search(r"p(\d+\.\d+)_q(\d+\.\d+)", filename)
        if match:
            p_born = float(match.group(1))
            p_die = float(match.group(2))

        # Handle the nested structure from sim_px_qy.json files
        if "results" in data:
            metadata = data.get("metadata", {})
            p_born = metadata.get("pBorn", p_born)
            p_die = metadata.get("pDie", p_die)
            trials = metadata.get("trials", trials)
            timestamp = metadata.get(
                "timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            # Get the first result
            result_key = next(iter(data["results"]))
            result = data["results"][result_key]

            if isinstance(result, dict) and "counts" in result:
                counts = result.get("counts", {})
                trials = sum(counts.values()) if not trials else trials
                stats = result.get("stats", {})

                # Get summary stats directly from the file
                summary = stats.get("summary", {})
                mode_relation = summary.get("mode")

                # Ensure we have JS divergences
                js_comparisons = {}
                for model, comp_data in stats.get("compare", {}).items():
                    js_comparisons[model] = comp_data.get("js", 0)

                # Find best fit model
                best_fit = stats.get("best_fit", "N/A")
                best_fit_js = min(js_comparisons.values()) if js_comparisons else 0

                # Convert to our expected format with all required statistics
                simulation_data = {
                    "distribution": {k: v / trials for k, v in counts.items()},
                    "raw_counts": counts,
                    "parameters": {"p_born": p_born, "p_die": p_die, "trials": trials},
                    "stats": {
                        "mode": mode_relation,
                        "mode_name": RELATION_NAMES.get(mode_relation, "Unknown"),
                        "stddev": summary.get("stddev", 0),
                        "entropy": summary.get("entropy", 0),
                        "gini": summary.get("gini", 0),
                        "coverage": summary.get("coverage", 0),
                        "best_fit": best_fit,
                        "best_fit_js": best_fit_js,
                        "js_uniform": js_comparisons.get("Uniform", 0),
                        "js_fv": js_comparisons.get("F-V", 0),
                        "js_suliman": js_comparisons.get("Suliman", 0),
                        "timestamp": timestamp,
                    },
                }

                # Create success message
                success_message = dbc.Alert(
                    [
                        html.P(f"Successfully loaded {filename}", className="mb-0"),
                        html.Small(
                            f"Parameters: p_born={p_born}, p_die={p_die}, trials={trials}"
                        ),
                    ],
                    color="success",
                    dismissable=True,
                    duration=4000,
                )

                return simulation_data, success_message, p_born, p_die, trials

        # If we couldn't process the file as a simulation
        return (
            dash.no_update,
            dbc.Alert(
                "File has an unrecognized format. Expected simulation data with 'results'.",
                color="warning",
                dismissable=True,
                duration=4000,
            ),
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    except Exception as e:
        error_message = dbc.Alert(
            f"Error processing file: {str(e)}",
            color="danger",
            dismissable=True,
            duration=4000,
        )
        return (
            dash.no_update,
            error_message,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )


# Add a new upload component for composition tab
dbc.Card(
    [
        dbc.CardHeader("Load Previous Results"),
        dbc.CardBody(
            [
                html.P("Upload previously saved JSON results:"),
                dcc.Upload(
                    id="upload-comp-json",
                    children=html.Div(
                        [
                            "Drag and Drop or ",
                            html.A("Select File"),
                        ]
                    ),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin-bottom": "10px",
                    },
                    multiple=False,
                    accept="application/json",
                ),
                html.Div(id="upload-comp-json-status"),
                html.Small(
                    "Files should be named comp_p[value]_q[value].json",
                    className="text-muted d-block mt-2",
                ),
            ]
        ),
    ],
    className="mt-3 mb-3",
),

# Add a new upload component for matrix tab
dbc.Card(
    [
        dbc.CardHeader("Load Previous Results"),
        dbc.CardBody(
            [
                html.P("Upload previously saved JSON results:"),
                dcc.Upload(
                    id="upload-matrix-json",
                    children=html.Div(
                        [
                            "Drag and Drop or ",
                            html.A("Select File"),
                        ]
                    ),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin-bottom": "10px",
                    },
                    multiple=False,
                    accept="application/json",
                ),
                html.Div(id="upload-matrix-json-status"),
                html.Small(
                    "Files should be named comp_p[value]_q[value].json",
                    className="text-muted d-block mt-2",
                ),
            ]
        ),
    ],
    className="mt-3 mb-3",
),


# Add a new upload component for matrix tab
dbc.Card(
    [
        dbc.CardHeader("Load Previous Results"),
        dbc.CardBody(
            [
                html.P("Upload previously saved JSON results:"),
                dcc.Upload(
                    id="upload-matrix-json",
                    children=html.Div(
                        [
                            "Drag and Drop or ",
                            html.A("Select File"),
                        ]
                    ),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin-bottom": "10px",
                    },
                    multiple=False,
                    accept="application/json",
                ),
                html.Div(id="upload-matrix-json-status"),
                html.Small(
                    "Files should be named comp_p[value]_q[value].json",
                    className="text-muted d-block mt-2",
                ),
            ]
        ),
    ],
    className="mt-3 mb-3",
),


# Add a callback for the composition tab JSON upload
@app.callback(
    Output("composition-results", "data", allow_duplicate=True),
    Output("upload-comp-json-status", "children"),
    Output("comp-p-born-input", "value", allow_duplicate=True),
    Output("comp-p-die-input", "value", allow_duplicate=True),
    Output("comp-trials-input", "value", allow_duplicate=True),
    Output("relation1-dropdown", "value", allow_duplicate=True),
    Output("relation2-dropdown", "value", allow_duplicate=True),
    Input("upload-comp-json", "contents"),
    State("upload-comp-json", "filename"),
    prevent_initial_call=True,
)
def process_uploaded_comp_json(contents, filename):
    """Process uploaded JSON file and update app state for composition tab"""
    if contents is None:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    try:
        # Decode the base64 encoded file contents
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        data = json.loads(decoded.decode("utf-8"))

        # Check if this is a composition file
        is_comp_file = filename.startswith("comp_") or "compositions" in data

        if not is_comp_file:
            return (
                dash.no_update,
                dbc.Alert(
                    f"File format not recognized as composition data: {filename}",
                    color="warning",
                    dismissable=True,
                    duration=4000,
                ),
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )

        # Extract p and q from filename using regex if available
        p_born = 0.5
        p_die = 0.5
        match = re.search(r"p(\d+\.\d+)_q(\d+\.\d+)", filename)
        if match:
            p_born = float(match.group(1))
            p_die = float(match.group(2))
        else:
            # Try to get from data
            p_born = data.get("pBorn", 0.5)
            p_die = data.get("pDie", 0.5)

        trials = data.get("trials", 100000)

        # Find a composition pair to display by default
        r1 = ALLEN_RELATIONS[0]
        r2 = ALLEN_RELATIONS[0]

        if "compositions" in data:
            # Find the first non-empty composition
            for rel1 in data["compositions"]:
                for rel2 in data["compositions"][rel1]:
                    if data["compositions"][rel1][rel2]:
                        r1 = rel1
                        r2 = rel2
                        break
                if r1 != ALLEN_RELATIONS[0]:
                    break

            # Construct result for a specific composition
            composition = data["compositions"].get(r1, {}).get(r2, {})
            if composition:
                # Calculate total count for this composition
                total_count = sum(item["count"] for item in composition.values())

                # Format as expected by our app
                composition_data = {
                    "r1": r1,
                    "r2": r2,
                    "r1_name": RELATION_NAMES.get(r1, "Unknown"),
                    "r2_name": RELATION_NAMES.get(r2, "Unknown"),
                    "parameters": {
                        "p_born": p_born,
                        "p_die": p_die,
                        "trials": trials,
                        "valid_count": data.get("valid_runs", trials),
                    },
                    "composition": {
                        rel: {"count": comp["count"], "percentage": comp["percentage"]}
                        for rel, comp in composition.items()
                    },
                    "total_count": total_count,
                    # Store the full compositions data for browsing
                    "all_compositions": data["compositions"],
                }

                # Create success message
                success_message = dbc.Alert(
                    [
                        html.P(f"Successfully loaded {filename}", className="mb-0"),
                        html.Small(
                            f"Parameters: p_born={p_born}, p_die={p_die}, composition: {r1}•{r2}"
                        ),
                    ],
                    color="success",
                    dismissable=True,
                    duration=4000,
                )

                return composition_data, success_message, p_born, p_die, trials, r1, r2

        # If no valid composition found
        return (
            dash.no_update,
            dbc.Alert(
                "No valid composition data found in the file",
                color="warning",
                dismissable=True,
                duration=4000,
            ),
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    except Exception as e:
        error_message = dbc.Alert(
            f"Error processing file: {str(e)}",
            color="danger",
            dismissable=True,
            duration=4000,
        )
        return (
            dash.no_update,
            error_message,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )


# Add a callback for the matrix tab JSON upload
@app.callback(
    Output("matrix-results", "data", allow_duplicate=True),
    Output("upload-matrix-json-status", "children"),
    Output("matrix-p-born-input", "value", allow_duplicate=True),
    Output("matrix-p-die-input", "value", allow_duplicate=True),
    Output("matrix-trials-input", "value", allow_duplicate=True),
    Input("upload-matrix-json", "contents"),
    State("upload-matrix-json", "filename"),
    prevent_initial_call=True,
)
def process_uploaded_matrix_json(contents, filename):
    """Process uploaded JSON file and update app state for matrix tab"""
    if contents is None:
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    try:
        # Decode the base64 encoded file contents
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        data = json.loads(decoded.decode("utf-8"))

        # Check if this is a matrix file OR a composition file (which can be converted)
        is_matrix_file = filename.startswith("matrix_") or "matrix" in data
        is_comp_file = filename.startswith("comp_") or "compositions" in data

        if not is_matrix_file and not is_comp_file:
            return (
                dash.no_update,
                dbc.Alert(
                    f"File format not recognized. Expected matrix or composition data.",
                    color="warning",
                    dismissable=True,
                    duration=4000,
                ),
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )

        # Extract p and q from filename using regex if available
        p_born = 0.5
        p_die = 0.5
        match = re.search(r"p(\d+\.\d+)_q(\d+\.\d+)", filename)
        if match:
            p_born = float(match.group(1))
            p_die = float(match.group(2))
        else:
            # Try to get from data
            p_born = data.get("pBorn", data.get("p_born", 0.5))
            p_die = data.get("pDie", data.get("p_die", 0.5))

        trials = data.get("trials", 100000)

        # If we have composition data but not matrix data, convert it
        if is_comp_file and "compositions" in data and not "matrix" in data:
            # Create a matrix structure from composition data
            matrix_data = {
                "matrix": {},
                "parameters": {"p_born": p_born, "p_die": p_die, "trials": trials},
                "timestamp": data.get(
                    "timestamp", datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                ),
            }

            # Convert the compositions data to matrix format
            compositions = data.get("compositions", {})

            # Initialize global stats for calculating distribution
            global_counts = {}
            total_compositions = 0

            # Process each composition pair
            for r1 in compositions:
                if r1 not in matrix_data["matrix"]:
                    matrix_data["matrix"][r1] = {}

                for r2 in compositions[r1]:
                    cell_data = {"composition": {}, "total": 0}
                    r3_data = compositions[r1][r2]

                    # Sum up the total counts for this cell
                    cell_total = sum(item["count"] for item in r3_data.values())
                    cell_data["total"] = cell_total
                    total_compositions += cell_total

                    # Process each resulting relation
                    for r3, details in r3_data.items():
                        cell_data["composition"][r3] = {
                            "count": details["count"],
                            "percentage": details["percentage"],
                        }
                        # Add to global counts
                        if r3 not in global_counts:
                            global_counts[r3] = 0
                        global_counts[r3] += details["count"]

                    matrix_data["matrix"][r1][r2] = cell_data

            # Add global statistics
            if total_compositions > 0:
                distribution = {
                    r: count / total_compositions for r, count in global_counts.items()
                }
                matrix_data["global_stats"] = {
                    "distribution": distribution,
                    "raw_counts": global_counts,
                    "entropy": entropy(list(distribution.values())),
                    "gini": gini_coefficient(list(distribution.values())),
                    # Other metrics could be added here
                }

            data = matrix_data

        # Create success message
        success_message = dbc.Alert(
            [
                html.P(f"Successfully loaded {filename}", className="mb-0"),
                html.Small(
                    f"Parameters: p_born={p_born}, p_die={p_die}, trials={trials}"
                ),
            ],
            color="success",
            dismissable=True,
            duration=4000,
        )

        return data, success_message, p_born, p_die, trials

    except Exception as e:
        error_message = dbc.Alert(
            f"Error processing file: {str(e)}",
            color="danger",
            dismissable=True,
            duration=4000,
        )
        return (
            dash.no_update,
            error_message,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )


# Update the existing upload component in Simulation tab to include help text
dbc.Card(
    [
        dbc.CardHeader("Load Previous Results"),
        dbc.CardBody(
            [
                html.P("Upload previously saved JSON results:"),
                dcc.Upload(
                    id="upload-json",
                    children=html.Div(
                        [
                            "Drag and Drop or ",
                            html.A("Select File"),
                        ]
                    ),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin-bottom": "10px",
                    },
                    multiple=False,
                    accept="application/json",
                ),
                html.Div(id="upload-json-status"),
                html.Small(
                    "Files should be named sim_p[value]_q[value].json",
                    className="text-muted d-block mt-2",
                ),
            ]
        ),
    ],
    className="mt-3 mb-3",
),


# Add a callback to update matrix visualization from loaded data
@app.callback(
    Output("matrix-status", "children", allow_duplicate=True),
    Output("matrix-global-stats", "children", allow_duplicate=True),
    Input("matrix-results", "data"),
    prevent_initial_call=True,
)
def update_matrix_status_from_upload(data):
    """Update the matrix status when data is loaded from a file"""
    if not data or not isinstance(data, dict):
        return dash.no_update, dash.no_update

    # Create a status card showing the data has been loaded
    status = html.Div(
        [
            dbc.Alert(
                [
                    html.H6("Matrix data loaded from file", className="alert-heading"),
                    html.Div(
                        [
                            html.P(
                                [
                                    html.Strong("Generated: "),
                                    data.get("timestamp", "Unknown"),
                                ],
                                className="mb-1",
                            ),
                            html.P(
                                [
                                    html.Strong("Birth Probability (p): "),
                                    f"{data.get('parameters', {}).get('p_born', 0.5)}",
                                ],
                                className="mb-1",
                            ),
                            html.P(
                                [
                                    html.Strong("Death Probability (q): "),
                                    f"{data.get('parameters', {}).get('p_die', 0.5)}",
                                ],
                                className="mb-1",
                            ),
                        ]
                    ),
                ],
                color="info",
                className="mt-3",
            )
        ]
    )

    # Update global stats if available
    if "global_stats" in data:
        global_stats = update_matrix_global_stats(data)
        return status, global_stats

    # Return placeholder if no global stats
    placeholder_stats = html.Div("Global statistics not available in the loaded file")
    return status, placeholder_stats


app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Allen Interval Probabilities</title>
        {%favicon%}
        {%css%}
        <style>
            .composition-reference details summary {
                padding: 8px;
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                cursor: pointer;
                margin-bottom: 8px;
            }
            .composition-reference table {
                font-size: 0.8rem;
            }
            .composition-reference th, .composition-reference td {
                text-align: center;
                padding: 3px 5px;
            }
            /* Make the table scrollable horizontally */
            .composition-reference .overflow-auto {
                overflow-x: auto;
                width: 100%;
            }

            /* Add Alspaugh's table styles here */
            table.composition td, table.composition th {
              padding-left: .12em;  padding-right: .12em;
              font-size: .90em;
            }
            td        {  text-align: center;  }
            td.full   {  font-style: italic;  }
            td.concur {  font-style: italic;  }

            td.p      {  font-family: sans-serif;  background-color:  #eef;  }
            td.P      {  font-family: sans-serif;  background-color:  #ccf;  }
            td.d      {  font-family: sans-serif;  background-color:  #fee;  }
            td.D      {  font-family: sans-serif;  background-color:  #fcc;  }
            td.osd    {  font-family: sans-serif;  background-color:  #efe;  }
            td.DSO    {  font-family: sans-serif;  background-color:  #cfc;  }

            td.oFD    {  font-family: sans-serif;  background-color:  #ddf;  }
            td.dfO    {  font-family: sans-serif;  background-color:  #bbf;  }
            td.m      {  font-family: sans-serif;  background-color:  #fdd;  }
            td.M      {  font-family: sans-serif;  background-color:  #fbb;  }
            td.pmosd  {  font-family: sans-serif;  background-color:  #dfd;  }
            td.DSOMP  {  font-family: sans-serif;  background-color:  #bfb;  }

            td.pmoFD  {  font-family: sans-serif;  background-color:  #ffb;  }
            td.dfOMP  {  font-family: sans-serif;  background-color:  #ff8;  }
            td.o      {  font-family: sans-serif;  background-color:  #fbf;  }
            td.O      {  font-family: sans-serif;  background-color:  #f8f;  }
            td.pmo    {  font-family: sans-serif;  background-color:  #bff;  }
            td.OMP    {  font-family: sans-serif;  background-color:  #8ff;  }

            td.s      {  font-family: sans-serif;  background-color:  #edb;  }
            td.S      {  font-family: sans-serif;  background-color:  #eb9;  }
            td.f      {  font-family: sans-serif;  background-color:  #deb;  }
            td.F      {  font-family: sans-serif;  background-color:  #be9;  }
            td.seS    {  font-family: sans-serif;  background-color:  #bed;  }
            td.Fef    {  font-family: sans-serif;  background-color:  #9eb;  }
            td.e      {  font-family: sans-serif;  background-color:  #d9c;  }
            td.concur {  background-color:  #bde;  }
            td.full   {  background-color:  #9be;  }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)
