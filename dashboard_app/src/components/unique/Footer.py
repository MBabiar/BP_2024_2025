import dash_bootstrap_components as dbc
from dash import html

from dashboard_app.src.constants import colors


class Footer(dbc.Row):
    """
    A footer component for the dashboard displaying copyright information.
    """

    def __init__(
        self,
    ):
        super().__init__(
            dbc.Col(
                html.Footer(
                    html.P(
                        "Cat database dashboard © 2025",
                        className="text-center py-4 mb-4",
                        style={"color": colors.TEXT_PRIMARY},
                    )
                )
            )
        )
