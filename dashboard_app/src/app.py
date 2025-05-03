import argparse
import os

import dash
import dash_bootstrap_components as dbc
import flask
from dash import dcc

from dashboard_app.src.callbacks import register_all_callbacks
from dashboard_app.src.components.unique.db_status_alert import create_db_status_alert
from dashboard_app.src.components.unique.Footer import Footer
from dashboard_app.src.components.unique.navbar import MainNavbar
from dashboard_app.src.constants import colors
from dashboard_app.src.utils.cache import init_cache
from dashboard_app.src.utils.logger import logger

# --------------------------------------------------
# Application configuration
# --------------------------------------------------
parser = argparse.ArgumentParser(description="Cat Database Dashboard")
parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
args = parser.parse_args()

logger.set_verbose(args.verbose)
logger.info(f"Starting application (verbose mode: {'enabled' if args.verbose else 'disabled'})")


# --------------------------------------------------
# Application initialization
# --------------------------------------------------
server = flask.Flask(__name__)

app = dash.Dash(
    __name__,
    server=server,
    title="Cat Database Dashboard",
    external_stylesheets=[dbc.themes.FLATLY],
    use_pages=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

cache = init_cache(app)
db_alert, db_healthy = create_db_status_alert()


# --------------------------------------------------
# Layout configuration
# --------------------------------------------------
app.layout = dbc.Container(
    children=[
        MainNavbar(),
        db_alert,
        # Main content area - filled by page content
        dbc.Row(
            dbc.Col(
                dash.page_container,
                width=12,
            ),
            className="px-4 my-4",
            style={"min-height": "calc(100vh - 80px - 24px - 72px)"},
        ),
        Footer(),
        dcc.Store(id="tree-file-store", data={}),
        dcc.Store(id="db-connection-state", data={"healthy": db_healthy}),
        dcc.Interval(id="db-check-interval", interval=5 * 1000, n_intervals=0),
        dcc.Store(id="cat-search-store", data=[]),
        dcc.Store(id="selected-cat-store", data=None),
    ],
    fluid=True,
    className="px-0",
    style={
        "background-color": colors.APP_BACKGROUND,
        "overflow-x": "hidden",
        "min-height": "100vh",
    },
)


# --------------------------------------------------
# Registering callbacks
# --------------------------------------------------
register_all_callbacks(app)


# --------------------------------------------------
# Application entry point
# --------------------------------------------------
if __name__ == "__main__":
    """
    Entry point when running the application directly.
    """
    in_docker = os.environ.get("RUNNING_IN_DOCKER", "false").lower() == "true"

    if in_docker:
        logger.info("Running in Docker environment")
        app.run(
            host="0.0.0.0",
            port=8080,
        )
    else:
        logger.info("Running in local environment")
        app.run(
            host="127.0.0.1",
            port=8080,
            debug=True,
            dev_tools_ui=True,
            dev_tools_props_check=True,
            dev_tools_hot_reload=True,
            dev_tools_hot_reload_interval=1000,
        )
