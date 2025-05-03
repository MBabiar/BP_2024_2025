import dash_bootstrap_components as dbc

from dashboard_app.src.constants import colors


class BasicCard(dbc.Card):
    def __init__(
        self,
        title: str,
        children=None,
        min_height: str = "100px",
        card_header_style: dict = {},
        card_body_style: dict = {},
        card_style: dict = {},
        card_header_class_name: str = "",
        card_body_class_name: str = "",
        card_class_name: str = "",
    ):
        """
        Initialize a basic card component with a title and optional children.
        Custom styles can be applied to the card header, body, and the card itself.

        Args:
            title (str): The title to display in the card header.
            children (_type_, optional): The content to display inside the card body. Defaults to None.
            min_height (str, optional): Minimum height for the card body. Defaults to "100px".
            card_header_style (dict, optional): Custom styles for the card header. Defaults to {}.
            card_body_style (dict, optional): Custom styles for the card body. Defaults to {}.
            card_style (dict, optional): Custom styles for the card itself. Defaults to {}.
            card_header_class_name (str, optional): Additional class names for the card header. Defaults to "".
            card_body_class_name (str, optional): Additional class names for the card body. Defaults to "".
            card_class_name (str, optional): Additional class names for the card. Defaults to "".
        """

        content = children if children is not None else []

        default_header_style = {
            "background-color": colors.CARD_HEADER,
            "font-weight": "bold",
            "border-bottom": f"2px solid {colors.BORDER_COLOR}",
        }

        default_body_style = {
            "min-height": min_height,
        }

        default_card_style = {
            "border": f"2px solid {colors.BORDER_COLOR}",
            "height": "100%",
            "max-height": "1000px",
        }

        final_header_style = default_header_style.copy()
        final_header_style.update(card_header_style)

        final_body_style = default_body_style.copy()
        final_body_style.update(card_body_style)

        final_card_style = default_card_style.copy()
        final_card_style.update(card_style)

        super().__init__(
            children=[
                dbc.CardHeader(
                    title,
                    style=final_header_style,
                    className=card_header_class_name,
                ),
                dbc.CardBody(
                    content,
                    className=card_body_class_name,
                    style=final_body_style,
                ),
            ],
            className=card_class_name,
            style=final_card_style,
        )
