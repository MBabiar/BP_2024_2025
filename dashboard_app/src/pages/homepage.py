import dash
import dash_bootstrap_components as dbc
from dash import html

from dashboard_app.src.components.reusable.MetricCard import MetricCard
from dashboard_app.src.constants import colors

dash.register_page(__name__, path="/", title="Home", name="Home")


def layout() -> list:
    """
    Create the homepage layout with welcome message and key statistics.

    Returns:
        list: List of Dash components making up the homepage
    """
    return [
        dbc.Row(
            # --------------------------------------------------
            # Welcome message card
            # --------------------------------------------------
            dbc.Col(
                dbc.Card(
                    [
                        html.H1("Cat Database Dashboard", className="display-4 mb-3"),
                        html.P(
                            "Welcome to the comprehensive cat database explorer. Find statistics and insights about cats from around the world.",
                            className="lead mb-4",
                        ),
                    ],
                    className="text-center p-3",
                    style={
                        "color": colors.TEXT_PRIMARY,
                        "background-color": colors.CARD_BACKGROUND_OPACITY,
                        "width": "fit-content",
                    },
                ),
                style={"justify-items": "center", "align-items": "center"},
            ),
            className="mb-4",
        ),
        # --------------------------------------------------
        # Statistics cards row
        # --------------------------------------------------
        dbc.Row(
            [
                dbc.Col(MetricCard("Total cats", id_value="total-cats"), width=3),
                dbc.Col(MetricCard("Total breeds", id_value="total-breeds"), width=3),
                dbc.Col(MetricCard("Total countries", id_value="total-countries"), width=3),
                dbc.Col(MetricCard("Total databases", id_value="total-source-dbs"), width=3),
            ],
        ),
        # --------------------------------------------------
        # Cat image
        # --------------------------------------------------
        dbc.Row(
            dbc.CardImg(
                src="/assets/cats.png",
                style={
                    "height": "700px",
                    "object-fit": "cover",
                    "object-position": "center 50%",
                    "overflow": "hidden",
                },
            )
        ),
    ]
