import dash_bootstrap_components as dbc

from dashboard_app.src.data.db_connector import Neo4jConnector
from dashboard_app.src.utils.cache import clear_cache


def create_db_status_alert() -> tuple[dbc.Row, bool]:
    """
    Create a database connection status alert component.

    Returns:
        tuple[dbc.Row, bool]: A tuple containing the alert component wrapped in a row
                             and the database health status boolean
    """
    db = Neo4jConnector()
    db_healthy = db.check_connection()

    if not db_healthy:
        clear_cache()

    message = "Database connected successfully" if db_healthy else "Database connection failed"
    alert_color = "success" if db_healthy else "danger"

    alert = dbc.Alert(
        id="db-status-alert",
        children=message,
        color=alert_color,
        dismissable=False,
        is_open=True,
        style={
            "display": "none" if db_healthy else "block",
        },
        className="mt-4",
    )

    alert_row = dbc.Row(
        dbc.Col(alert, width=12),
        className="px-4",
    )

    return alert_row, db_healthy
