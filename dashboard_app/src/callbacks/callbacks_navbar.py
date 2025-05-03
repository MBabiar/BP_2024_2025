from dash.dependencies import Input, Output, State


def register_navbar_callbacks(app) -> None:
    """
    Register navbar callbacks for interactivity.

    Args:
        app: The Dash application instance to register callbacks with

    Returns:
        None
    """

    @app.callback(
        Output("navbar-collapse", "is_open"),
        Input("navbar-toggler", "n_clicks"),
        State("navbar-collapse", "is_open"),
    )
    def toggle_navbar_collapse(n: int, is_open: bool) -> bool:
        """
        Toggle the navbar collapse state on mobile devices.

        Args:
            n (int): Number of times the toggle button has been clicked
            is_open (bool): Current state of the navbar collapse

        Returns:
            bool: Updated state of navbar collapse (True = open, False = closed)
        """
        if n:
            return not is_open
        return is_open
