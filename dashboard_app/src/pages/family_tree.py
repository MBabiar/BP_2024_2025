import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard_app.src.components.reusable.BasicCard import BasicCard
from dashboard_app.src.components.reusable.GraphCard import GraphCard
from dashboard_app.src.components.reusable.PrimaryButton import PrimaryButton
from dashboard_app.src.components.unique.search import create_cat_search

dash.register_page(__name__, path="/family-tree", title="Family tree", name="Family tree", order=2)


def layout() -> list:
    """
    Create the family tree visualization page layout with search and interactive controls.

    Returns:
        list: List of Dash components making up the family tree visualization page
    """
    return [
        dbc.Row(
            [
                # --------------------------------------------------
                # Left column: Search and settings
                # --------------------------------------------------
                dbc.Col(
                    [
                        html.Div(
                            [
                                BasicCard(
                                    title="Search for a cat",
                                    children=[
                                        dcc.Dropdown(id="cat-selector", style={"display": "none"}),
                                        create_cat_search(),
                                        PrimaryButton(
                                            text="Generate Family tree",
                                            id="generate-tree-button",
                                        ),
                                    ],
                                    min_height="100px",
                                ),
                                BasicCard(
                                    title="Family tree settings",
                                    children=[
                                        html.P("Depth of tree:", className="mb-0"),
                                        dbc.Input(
                                            id="tree-depth-input",
                                            type="number",
                                            min=1,
                                            max=1000,
                                            step=1,
                                            value=3,
                                        ),
                                        html.P(
                                            "Maximum recommended depth is 10, as larger values are slower to render and less visually clear.",
                                            className="text-muted fst-italic small mt-1 mb-0",
                                        ),
                                    ],
                                    min_height="100px",
                                    card_body_class_name="py-2",
                                ),
                            ],
                            className="d-flex flex-column h-100 gap-4",
                        ),
                    ],
                    sm=12,
                    md=3,
                ),
                # --------------------------------------------------
                # Right column: Family tree visualization
                # --------------------------------------------------
                dbc.Col(
                    [
                        GraphCard(
                            title="Family tree visualization",
                            children=[
                                html.Iframe(id="family-tree-graph"),
                                html.Div(id="family-tree-info"),
                            ],
                            min_height="100px",
                            card_body_style={
                                "align-content": "center",
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
            ]
        ),
    ]
