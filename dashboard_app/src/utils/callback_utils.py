import plotly.graph_objects as go

from dashboard_app.src.constants import colors
from dashboard_app.src.utils.logger import logger


def create_error_figure(error_text: str) -> go.Figure:
    """
    Create error figure with message

    Args:
        error_text (str): Error message to display

    Returns:
        go.Figure: Figure object with error message
    """
    fig = go.Figure()
    fig.update_layout(
        annotations=[
            {
                "text": error_text,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16, "color": colors.DANGER},
            }
        ]
    )
    return fig


def skip_cache_when_db_unhealthy(f, *args, **kwargs):
    """
    Skip caching when database is unhealthy.

    Args:
        f: The function being cached
        *args: The arguments to the function
        **kwargs: The keyword arguments to the function

    Returns:
        bool: True if caching should be skipped
    """
    if args and len(args) > 0:
        db_state = None
        for arg in args:
            if isinstance(arg, dict) and "healthy" in arg.keys():
                db_state = arg
                break

        if not db_state:
            return False

        healthy = db_state.get("healthy", False)

        if not healthy:
            logger.warning("⚠️ Database is unhealthy. Skipping cache.")

        return not healthy
    return False
