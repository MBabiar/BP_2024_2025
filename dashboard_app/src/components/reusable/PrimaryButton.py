import dash_bootstrap_components as dbc

from dashboard_app.src.constants import colors


class PrimaryButton(dbc.Button):
    def __init__(
        self,
        text: str,
        id: str,
        color: str = "primary text-black",
        className: str = "",
        style: dict = {"background-color": colors.PRIMARY},
    ):
        """
        Initialize a primary button with custom styles and properties.

        Args:
            text (str): The text to display on the button.
            id (str): The ID to assign to the button for callback purposes.
            color (str): The color of the button. Default is "primary text-black".
            className (str): Additional CSS classes to apply to the button. Default is an empty string.
            style (dict): Additional styles to apply to the button. Default is a dictionary with a background color.
        """
        super().__init__(
            text,
            id=id,
            color=color,
            className="border-0 " + className,
            style=style,
        )
