import dash_bootstrap_components as dbc
from dash import html

from dashboard_app.src.components.reusable.BasicInput import BasicInput
from dashboard_app.src.components.reusable.PrimaryButton import PrimaryButton
from dashboard_app.src.constants import colors


def create_cat_search() -> html.Div:
    """
    Create cat search component with input field, search button, and results display.

    Returns:
        html.Div: A Dash component containing the complete search UI with input field,
                 search button, selected cat display, and search results area
    """
    return html.Div(
        children=[
            # --------------------------------------------------
            # Search input field and search button
            # --------------------------------------------------
            BasicInput(
                id="cat-search-input",
                type="text",
                placeholder="Enter cat name or ID...",
                className="mb-2",
            ),
            PrimaryButton(
                text="Search",
                id="cat-search-button",
            ),
            html.Hr(className="mt-3 mb-2"),
            # --------------------------------------------------
            # Currently selected cat display
            # --------------------------------------------------
            html.Div(
                children=[
                    html.P(
                        "Selected cat:",
                        className="mb-0",
                        style={"font-weight": "bold"},
                    ),
                    html.Div(
                        id="selected-cat-info",
                        className="selected-cat-container py-2 px-3",
                        style={
                            "border": f"1px solid {colors.BORDER_COLOR}",
                            "borderRadius": "5px",
                            "minHeight": "40px",
                        },
                    ),
                ],
                className="mb-2",
            ),
            # --------------------------------------------------
            # Search results display
            # --------------------------------------------------
            html.P(
                "Search results:",
                className="mb-0",
                style={"font-weight": "bold"},
            ),
            dbc.Spinner(
                html.Div(
                    id="cat-search-results",
                    style={
                        "maxHeight": "200px",
                        "overflowY": "auto",
                        "border": f"1px solid {colors.BORDER_COLOR}",
                        "borderRadius": "5px",
                        "minHeight": "40px",
                    },
                    className="p-2 mb-2",
                ),
                color=colors.INFO,
            ),
        ]
    )
