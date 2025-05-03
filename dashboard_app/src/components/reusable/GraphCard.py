import dash_bootstrap_components as dbc
from dash import dcc, html

from dashboard_app.src.components.reusable.BasicCard import BasicCard
from dashboard_app.src.constants import colors


class GraphCard(BasicCard):
    """
    Custom card component for displaying graphs with loading indicators.

    Args:
        title (str): The title to be displayed in the card header.
        top_children (list, optional): Content to be placed above the loading section. Defaults to None.
        children (list, optional): The main content to be wrapped with a loading indicator. Defaults to None.
        min_height (str, optional): Minimum height for the card in CSS units. Defaults to "250px".
        card_header_class_name (str, optional): Additional CSS class names for the card header. Defaults to "".
        card_body_class_name (str, optional): Additional CSS class names for the card body. Defaults to "".
        card_class_name (str, optional): Additional CSS class names for the entire card. Defaults to "".
        card_header_style (dict, optional): Additional CSS styles for the card header. Defaults to {}.
        card_body_style (dict, optional): Additional CSS styles for the card body. Defaults to {}.
        card_style (dict, optional): Additional CSS styles for the entire card. Defaults to {}.
        loading_parent_style (dict, optional): Additional CSS styles for the loading parent container. Defaults to {}.
        loading_overlay_style (dict, optional): Additional CSS styles for the loading overlay. Defaults to {}.
    """

    def __init__(
        self,
        title: str,
        top_children=None,
        children=None,
        min_height: str = "250px",
        card_header_class_name: str = "",
        card_body_class_name: str = "",
        card_class_name: str = "",
        card_header_style: dict = {},
        card_body_style: dict = {},
        card_style: dict = {},
        loading_parent_style: dict = {},
        loading_overlay_style: dict = {},
    ):
        top_content = top_children if top_children is not None else []
        inner_content = children if children is not None else []

        default_loading_parent_style = {
            "min-height": min_height,
        }

        default_overlay_style = {
            "min-height": min_height,
        }

        final_loading_parent_style = default_loading_parent_style.copy()
        final_loading_parent_style.update(loading_parent_style)

        final_overlay_style = default_overlay_style.copy()
        final_overlay_style.update(loading_overlay_style)

        wrapped_content = dcc.Loading(
            children=inner_content,
            custom_spinner=html.Div(
                children=[
                    html.H5("Loading Data..."),
                    dbc.Spinner(size="lg", color=colors.PRIMARY),
                ],
                className="text-center py-5",
            ),
            parent_style=final_loading_parent_style,
            overlay_style=final_overlay_style,
        )

        final_content = top_content + [wrapped_content]

        super().__init__(
            title=title,
            children=final_content,
            min_height=min_height,
            card_header_style=card_header_style,
            card_body_style=card_body_style,
            card_style=card_style,
            card_header_class_name=card_header_class_name,
            card_body_class_name=card_body_class_name,
            card_class_name=card_class_name,
        )
