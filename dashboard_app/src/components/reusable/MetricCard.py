import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard_app.src.constants import colors


class MetricCard(dbc.Card):
    """
    A card component for displaying numeric metrics with titles and loading states.

    Parameters:
        title (str): Title text to display under the metric value
        id_value (str): ID for the metric value component to be used in callbacks
    """

    def __init__(
        self,
        title: str,
        id_value: str,
    ):
        super().__init__(
            dcc.Loading(
                children=[
                    html.H3(id=id_value, className="h3"),
                    html.P(title, className="h5"),
                ],
                type="circle",
                overlay_style={
                    "min-height": "60px",
                },
            ),
            body=True,
            className="mb-3",
            style={
                "background-color": colors.CARD_BACKGROUND_OPACITY,
            },
        )
