import dash_bootstrap_components as dbc


class BasicInput(dbc.Input):
    def __init__(
        self,
        id: str,
        type: str = "text",
        placeholder: str = "Enter text",
        className: str = "",
        style: dict = None,
    ):
        """
        Initialize a basic input field with custom styles and properties.

        Args:
            id (str): The ID to assign to the input field for callback purposes.
            type (str): The type of the input field (e.g., "text", "number"). Default is "text".
            placeholder (str): Placeholder text for the input field. Default is "Enter text".
            className (str): Additional CSS classes to apply to the input field. Default is an empty string.
            style (dict): Additional styles to apply to the input field. Default is None.
        """
        super().__init__(
            id=id,
            type=type,
            placeholder=placeholder,
            className=className,
            style=style,
        )
