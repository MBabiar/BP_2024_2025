import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard_app.src.components.reusable.GraphCard import GraphCard
from dashboard_app.src.constants import colors


class BreedDistributionChart(GraphCard):
    """
    A specialized GraphCard component for displaying breed distribution statistics with filter controls.

    The component includes filters for:
    - Showing all breeds vs. top N breeds
    - Filtering by count range
    - Toggling between linear and logarithmic y-axis scale
    """

    def __init__(self):
        top_content = [
            # --------------------------------------------------
            # Breed filter
            # --------------------------------------------------
            html.Div(
                children=[
                    # --------------------------------------------------
                    # Filter type options
                    # --------------------------------------------------
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label(
                                        "Filter options:",
                                        style={"font-weight": "bold"},
                                    ),
                                    dbc.RadioItems(
                                        id="breed-filter-type",
                                        options=[
                                            {"label": "Show all breeds", "value": "all"},
                                            {"label": "Show top breeds", "value": "top"},
                                            {"label": "Show by count range", "value": "range"},
                                        ],
                                        value="all",
                                        inline=True,
                                    ),
                                ],
                                width=12,
                            ),
                        ],
                    ),
                    # --------------------------------------------------
                    # Filter controls
                    # --------------------------------------------------
                    dbc.Row(
                        [
                            # --------------------------------------------------
                            # For top N breeds filter
                            # --------------------------------------------------
                            dbc.Col(
                                [
                                    html.Label(
                                        "Number of top breeds:",
                                        style={"font-weight": "bold"},
                                    ),
                                    dbc.Input(
                                        id="top-n-breeds",
                                        type="number",
                                        min=1,
                                        step=1,
                                        value=10,
                                        style={
                                            "border-color": colors.BORDER_COLOR,
                                        },
                                    ),
                                ],
                                id="top-breeds-controls",
                                width=6,
                            ),
                            # --------------------------------------------------
                            # For count range filter
                            # --------------------------------------------------
                            dbc.Col(
                                [
                                    html.Label(
                                        "Count range:",
                                        style={"font-weight": "bold"},
                                    ),
                                    dbc.InputGroup(
                                        [
                                            dbc.Input(
                                                id="min-count",
                                                type="number",
                                                placeholder="Min",
                                                min=0,
                                                value=0,
                                                style={
                                                    "borderColor": colors.BORDER_COLOR,
                                                    "borderRight": "none",
                                                },
                                            ),
                                            dbc.Input(
                                                id="max-count",
                                                type="number",
                                                placeholder="Max",
                                                style={
                                                    "border-color": colors.BORDER_COLOR,
                                                },
                                            ),
                                        ]
                                    ),
                                ],
                                id="range-controls",
                                width=6,
                            ),
                        ],
                        id="filter-controls-row",
                    ),
                    # --------------------------------------------------
                    # Y-axis scale toggle with visual styling
                    # --------------------------------------------------
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label(
                                        "Y-axis scale:",
                                        style={"font-weight": "bold"},
                                    ),
                                    dbc.RadioItems(
                                        id="breed-y-scale",
                                        options=[
                                            {"label": "Linear", "value": "linear"},
                                            {"label": "Logarithmic", "value": "log"},
                                        ],
                                        value="linear",
                                        inline=True,
                                    ),
                                ],
                                width=12,
                            ),
                        ],
                    ),
                ],
                className="mx-2 p-3 rounded d-grid gap-1",
                style={
                    "backgroundColor": colors.PLOT_BACKGROUND_COLOR,
                    "border": f"1px solid {colors.BORDER_COLOR}",
                },
            ),
        ]

        inner_content = [
            dcc.Graph(
                id="breed-chart",
                style={"display": "none"},
            )
        ]

        super().__init__(title="Breed distribution", top_children=top_content, children=inner_content)
