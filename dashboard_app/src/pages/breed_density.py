import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard_app.src.components.reusable.BasicCard import BasicCard
from dashboard_app.src.components.reusable.GraphCard import GraphCard
from dashboard_app.src.components.reusable.PrimaryButton import PrimaryButton

dash.register_page(__name__, path="/breed-density", title="Breed Density Map", name="Breed Density Map", order=3)


def layout() -> list:
    """
    Create the breed density map page layout with interactive controls and visualization.

    Returns:
        list: List of Dash components making up the breed density map page
    """
    return [
        dcc.Store(id="breed-density-load-trigger", data={"loaded": True}),
        dbc.Row(
            [
                # --------------------------------------------------
                # Controls and Information
                # --------------------------------------------------
                dbc.Col(
                    html.Div(
                        children=[
                            BasicCard(
                                title="Breed Selection",
                                children=[
                                    html.P("Select a breed to view its geographical distribution:"),
                                    html.Div(
                                        [
                                            html.Label("Select breed:", className="mb-2 fw-bold"),
                                            dcc.Dropdown(
                                                id="breed-selector",
                                                placeholder="Select a breed...",
                                                className="mb-3",
                                            ),
                                        ],
                                        id="breed-selector-container",
                                    ),
                                    PrimaryButton(
                                        text="Update Map",
                                        id="update-breed-density-button",
                                    ),
                                ],
                                min_height="100px",
                            ),
                            BasicCard(
                                title="About Breed Density",
                                children=[
                                    html.P(
                                        """The breed density map shows how a specific cat breed is distributed across different 
                                            countries. The map shows the concentration of the selected breed 
                                            relative to the total cat population in each country."""
                                    ),
                                    html.P(
                                        """Darker colors indicate higher density or concentration of the selected breed 
                                            in that region."""
                                    ),
                                ],
                                min_height="100px",
                            ),
                        ],
                        className="d-flex flex-column h-100 gap-4",
                    ),
                    sm=12,
                    md=3,
                ),
                # --------------------------------------------------
                # Visualization
                # --------------------------------------------------
                dbc.Col(
                    [
                        GraphCard(
                            title="Breed Density by Region",
                            children=[
                                dcc.Graph(id="breed-density-map", style={"display": "none"}),
                                html.Div(id="breed-density-info"),
                            ],
                            card_body_style={
                                "min-height": "550px",
                                "padding": "0",
                            },
                            loading_parent_style={
                                "height": "100%",
                                "align-content": "center",
                            },
                        ),
                    ],
                    sm=12,
                    md=9,
                ),
            ],
        ),
    ]
