import dash

from dashboard_app.src.callbacks.callbacks_breed_density import (
    register_callbacks as register_breed_density_callbacks,
)
from dashboard_app.src.callbacks.callbacks_breed_timeline import (
    register_callbacks as register_breed_timeline_callbacks,
)
from dashboard_app.src.callbacks.callbacks_database import register_callbacks as register_database_callbacks
from dashboard_app.src.callbacks.callbacks_family_tree import register_callbacks as register_family_tree_callbacks
from dashboard_app.src.callbacks.callbacks_general import register_callbacks as register_general_callbacks
from dashboard_app.src.callbacks.callbacks_navbar import register_navbar_callbacks


def register_all_callbacks(app: dash.Dash) -> None:
    """
    Register all callbacks for the dashboard application.

    Args:
        app (dash.Dash): The Dash application instance.

    Returns:
        None
    """
    register_database_callbacks(app)
    register_general_callbacks(app)
    register_family_tree_callbacks(app)
    register_breed_density_callbacks(app)
    register_breed_timeline_callbacks(app)
    register_navbar_callbacks(app)
