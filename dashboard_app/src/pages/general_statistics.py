import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard_app.src.components.reusable.GraphCard import GraphCard
from dashboard_app.src.components.unique.BreedDistributionChart import BreedDistributionChart

dash.register_page(__name__, path="/statistics", title="General Statistics", name="General Statistics", order=1)


def layout() -> list:
    """
    Create the general statistics page layout with interactive charts and controls.

    Returns:
        list: List of Dash components making up the general statistics page
    """
    return [
        dcc.Store(id="chart-load-trigger", data={"loaded": True}),
        dbc.Row(
            [
                # --------------------------------------------------
                # Breed distribution section
                # --------------------------------------------------
                dbc.Col(
                    BreedDistributionChart(),
                    md=12,
                    lg=7,
                ),
                # --------------------------------------------------
                # Gender and birth year charts
                # --------------------------------------------------
                dbc.Col(
                    [
                        html.Div(
                            [
                                GraphCard(
                                    title="Gender distribution",
                                    children=dcc.Graph(id="gender-chart", style={"display": "none"}),
                                    card_body_style={"max-height": "350px"},
                                    card_style={"max-height": "350px"},
                                ),
                                GraphCard(
                                    title="Birth year distribution",
                                    children=dcc.Graph(id="birth-year-chart", style={"display": "none"}),
                                    card_body_style={"max-height": "350px"},
                                    card_style={"max-height": "350px"},
                                ),
                            ],
                            className="d-flex flex-column h-100 gap-4",
                        )
                    ],
                    md=12,
                    lg=5,
                ),
            ],
            className="mb-4",
        ),
        # --------------------------------------------------
        # Country population map
        # --------------------------------------------------
        dbc.Row(
            [
                dbc.Col(
                    GraphCard(title="Country population", children=dcc.Graph(id="country-map")),
                    width=12,
                ),
            ],
            className="mb-4",
        ),
    ]


7
