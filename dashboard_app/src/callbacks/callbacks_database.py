from dash import Input, Output, no_update

from dashboard_app.src.data.db_connector import Neo4jConnector

db = Neo4jConnector()
previous_connection_state = None


def register_callbacks(app) -> None:
    """
    Register database-related callbacks for monitoring connection status.

    Args:
        app: The Dash application instance to register callbacks with

    Returns:
        None
    """

    # ----------------------------------------------------------------------------------------------------
    # Database Connection Status Check
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        [
            Output("db-status-alert", "color"),
            Output("db-status-alert", "style"),
            Output("db-connection-state", "data"),
        ],
        Input("db-check-interval", "n_intervals"),
    )
    def check_db_connection(_: int) -> tuple[str, str, dict, dict]:
        """
        Check database connection status periodically and update UI components.

        Args:
            _ (int): Number of intervals elapsed (not directly used)

        Returns:
            tuple: A tuple containing (alert message, alert color, alert style dictionary, connection state)
        """
        global previous_connection_state

        is_connected = db.check_connection()

        # Don't update UI if the connection state hasn't changed, this prevents flickering
        if previous_connection_state is not None and previous_connection_state == is_connected:
            if is_connected:
                return (
                    "success",
                    {"display": "none"},
                    no_update,
                )
            else:
                return (
                    "danger",
                    {"display": "block"},
                    no_update,
                )

        previous_connection_state = is_connected

        if is_connected:
            return (
                "success",
                {"display": "none"},
                {"healthy": True},
            )
        else:
            return (
                "danger",
                {"display": "block"},
                {"healthy": False},
            )
