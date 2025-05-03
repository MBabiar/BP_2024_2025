from dash import Input, Output, State, html
from plotly.graph_objects import Figure

from dashboard_app.src.callbacks.callbacks_database import db
from dashboard_app.src.constants import colors
from dashboard_app.src.utils.cache import CacheManager
from dashboard_app.src.utils.data_processing import process_breed_density_by_country, process_breed_distribution
from dashboard_app.src.utils.logger import logger
from dashboard_app.src.utils.visualization import create_breed_density_map


def register_callbacks(app):
    """
    Register callbacks for breed density visualization features.

    Args:
        app: The Dash application instance
    """

    # ----------------------------------------------------------------------------------------------------
    # Get breed list for dropdown
    # ----------------------------------------------------------------------------------------------------
    @CacheManager.memoize()
    def get_cached_breed_list() -> list:
        """
        Fetch and process breed list for dropdown with caching.

        Returns:
            list: List of dictionaries with label and value for dropdown
        """
        try:
            breed_data = db.get_breed_distribution()
            breed_df = process_breed_distribution(breed_data)

            if breed_df.empty:
                return []

            breed_df = breed_df.sort_values(by="count", ascending=False)

            options = [
                {"label": f"{row['breed']} ({row['count']} cats)", "value": row["breed"]}
                for _, row in breed_df.iterrows()
            ]

            return options
        except Exception as e:
            logger.error(f"Error fetching breed list: {e}")
            return []

    # ----------------------------------------------------------------------------------------------------
    # Populate breed selector dropdown
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        Output("breed-selector", "options"),
        Input("breed-density-load-trigger", "data"),
        State("db-connection-state", "data"),
    )
    def populate_breed_selector(_, db_state: dict) -> list:
        """
        Populate the breed selector dropdown with available breeds.

        Args:
            _ (dict): Trigger from the load trigger event (not used directly)
            db_state (dict): Dictionary containing database connection state

        Returns:
            list: List of dictionaries with label and value for dropdown
        """
        if not db_state.get("healthy", False):
            return []

        return get_cached_breed_list()

    # ----------------------------------------------------------------------------------------------------
    # Create cached breed density map
    # ----------------------------------------------------------------------------------------------------
    @CacheManager.memoize()
    def create_cached_breed_density_map(selected_breed: str) -> tuple[Figure, bool]:
        """
        Create a breed density map using the selected breed with caching.
        This function is only for creating the visualization and should only be called
        after all error checks have passed.

        Args:
            selected_breed (str): Selected breed code to create visualization for

        Returns:
            tuple: A tuple containing (Plotly figure, success flag)
        """
        try:
            breed_data = db.get_breed_density_by_country(selected_breed)
            breed_density_df = process_breed_density_by_country(breed_data)

            if breed_density_df.empty:
                return Figure(), False

            figure = create_breed_density_map(breed_density_df=breed_density_df, selected_breed=selected_breed)
            return figure, True

        except Exception as e:
            logger.error(f"Error creating breed density map: {e}")
            return Figure(), False

    # ----------------------------------------------------------------------------------------------------
    # Update breed density map - Parent function that handles error states and calls the cached function
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        [
            Output("breed-density-map", "figure"),
            Output("breed-density-info", "children"),
            Output("breed-density-map", "style"),
        ],
        Input("update-breed-density-button", "n_clicks"),
        [
            State("breed-selector", "value"),
            State("db-connection-state", "data"),
        ],
    )
    def update_breed_density_map(
        n_clicks: int, selected_breed: str, db_state: dict
    ) -> tuple[Figure, object, dict]:
        """
        Update the breed density map based on user selection.
        This parent function handles all error states and user messages,
        then calls the cached visualization function when conditions are met.

        Args:
            n_clicks (int): Number of times the update button has been clicked
            selected_breed (str): Selected breed code from dropdown
            db_state (dict): Dictionary containing database connection state

        Returns:
            tuple: A tuple containing (Plotly figure, info/error message component, graph style)
        """
        default_graph_style = {
            "display": "block",
        }

        hidden_graph_style = {
            "display": "none",
        }

        empty_figure = Figure()

        if n_clicks is None:
            return (
                empty_figure,
                html.H5(
                    "Select a breed and click 'Update Map' to visualize the breed density",
                    className="text-muted text-center my-3",
                ),
                hidden_graph_style,
            )

        if not selected_breed:
            return (
                empty_figure,
                html.Div(
                    [
                        html.Span("⚠️", style={"fontSize": "1.5rem", "color": colors.WARNING}),
                        html.H5(
                            "Please select a specific breed from the dropdown",
                            className="text-warning text-center mt-2",
                        ),
                    ],
                    className="text-center",
                ),
                hidden_graph_style,
            )

        if not db_state.get("healthy", False):
            return (
                empty_figure,
                html.Div(
                    [
                        html.Span("⚠️", style={"fontSize": "2rem"}),
                        html.H5("Database connection error - No data available", className="text-danger mt-2"),
                    ],
                    className="text-center",
                ),
                hidden_graph_style,
            )

        figure, success = create_cached_breed_density_map(selected_breed)

        if success:
            return figure, "", default_graph_style

        return (
            empty_figure,
            html.Div(
                [
                    html.Span("ℹ️", style={"fontSize": "1.5rem"}),
                    html.H5(
                        f"No distribution data available for breed: {selected_breed}", className="text-center py-2"
                    ),
                ],
                className="text-center",
            ),
            hidden_graph_style,
        )
