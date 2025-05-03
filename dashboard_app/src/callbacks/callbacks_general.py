import pandas as pd
from dash import Input, Output, State
from plotly.graph_objects import Figure

from dashboard_app.src.callbacks.callbacks_database import db
from dashboard_app.src.utils.cache import CacheManager
from dashboard_app.src.utils.callback_utils import create_error_figure
from dashboard_app.src.utils.data_processing import (
    process_birth_year_distribution,
    process_breed_distribution,
    process_country_distribution,
    process_gender_distribution,
)
from dashboard_app.src.utils.logger import logger
from dashboard_app.src.utils.visualization import (
    create_birth_year_line_chart,
    create_breed_bar_chart,
    create_country_map,
    create_gender_pie_chart,
)


def register_callbacks(app):
    """
    Register callbacks for general statistics tab

    This function sets up all Dash callbacks related to the General Statistics tab.

    Args:
        app: The Dash application instance
    """

    # ----------------------------------------------------------------------------------------------------
    # Summary Statistics
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        [
            Output("total-cats", "children"),
            Output("total-breeds", "children"),
            Output("total-countries", "children"),
            Output("total-source-dbs", "children"),
        ],
        Input("db-connection-state", "data"),
    )
    @CacheManager.memoize()
    def update_summary_stats(db_state: dict) -> tuple[str, str, str, str]:
        """
        Update summary statistics.

        Args:
            db_state: Dictionary containing database connection state

        Returns:
            tuple(str, str, str, str): Tuple containing formatted statistics (total cats, total breeds, total countries, total source DBs)
        """

        if not db_state.get("healthy", False):
            return "N/A", "N/A", "N/A", "N/A"

        try:
            total_cats = db.get_cat_count()
            total_breeds = db.get_breed_count()
            total_countries = db.get_country_count()
            total_source_dbs = db.get_source_db_count()

            return (
                f"{total_cats:,}",
                f"{total_breeds:,}",
                f"{total_countries:,}",
                f"{total_source_dbs:,}",
            )
        except Exception as e:
            logger.error(f"Error fetching summary stats: {e}")
            return "Error", "Error", "Error", "Error"

    # ----------------------------------------------------------------------------------------------------
    # Breed Chart
    # ----------------------------------------------------------------------------------------------------
    @CacheManager.memoize()
    def get_cached_breed_data() -> pd.DataFrame:
        """
        Fetch and process breed data with caching.

        This helper function retrieves breed distribution data from the database,
        processes it with the data_processing utility, and caches it.

        Returns:
            pd.DataFrame: Processed breed distribution DataFrame
        """

        try:
            breed_data = db.get_breed_distribution()
            return process_breed_distribution(breed_data)
        except Exception as e:
            logger.error(f"Error fetching breed data: {e}")
            return None

    @app.callback(
        [
            Output("top-breeds-controls", "style"),
            Output("range-controls", "style"),
        ],
        Input("breed-filter-type", "value"),
    )
    def toggle_filter_controls(filter_type: str) -> tuple[dict, dict]:
        """
        Show/hide appropriate filter controls based on selection

        This callback dynamically toggles the visibility of filter controls depending
        on the user's selection of filter type for the breed chart.

        Args:
            filter_type (str): The type of filter selected ('all', 'top', or 'range')

        Returns:
            tuple[dict, dict]: CSS style dictionaries for top breeds and range controls
                              to control their visibility
        """

        show_top_controls = {"display": "block"} if filter_type == "top" else {"display": "none"}
        show_range_controls = {"display": "block"} if filter_type == "range" else {"display": "none"}

        return show_top_controls, show_range_controls

    @app.callback(
        [
            Output("breed-chart", "figure"),
            Output("breed-chart", "style"),
        ],
        [
            Input("breed-filter-type", "value"),
            Input("top-n-breeds", "value"),
            Input("min-count", "value"),
            Input("max-count", "value"),
            Input("breed-y-scale", "value"),
            Input("chart-load-trigger", "data"),
        ],
        State("db-connection-state", "data"),
    )
    def update_breed_chart(
        filter_type: str, top_n: int, min_count: int, max_count: int, y_scale: str, _, db_state: dict
    ) -> Figure:
        """
        Update breed chart with selected filters using cached data

        This callback generates the breed distribution chart based on user-selected
        filtering options. It retrieves data from cache, applies the appropriate filters,
        and generates the chart.

        Args:
            filter_type (str): Type of filtering to apply ('all', 'top', or 'range')
            top_n (int): Number of top breeds to display when filter_type is 'top'
            min_count (int): Minimum count for range filtering
            max_count (int): Maximum count for range filtering (None for no upper limit)
            y_scale (str): Y-axis scale ('linear' or 'log')
            _ (dict): Chart load trigger (not used directly)
            db_state (dict): Dictionary containing database connection state

        Returns:
            Figure: A Plotly figure Figure for the chart
        """

        visible = {"display": "block"}

        if max_count == "" or max_count is None:
            max_count = None

        if not db_state.get("healthy", False):
            error_fig = create_error_figure("Database connection error - No data available")
            return error_fig, visible

        try:
            breed_df = get_cached_breed_data()

            if breed_df.empty:
                error_fig = create_error_figure("No breed data available")
                return error_fig, visible

            if filter_type == "top":
                breed_df = breed_df.sort_values(by="count", ascending=False).head(
                    top_n if top_n is not None else 10
                )
            elif filter_type == "range":
                if min_count > 0:
                    breed_df = breed_df[breed_df["count"] >= min_count]
                if max_count is not None:
                    breed_df = breed_df[breed_df["count"] <= max_count]

            breed_df = breed_df.sort_values(by="count", ascending=False)
            breed_chart = create_breed_bar_chart(breed_df=breed_df, filter_type=filter_type, y_scale=y_scale)
            return breed_chart, visible
        except Exception as e:
            logger.error(f"Error creating breed chart: {e}")
            error_fig = create_error_figure(f"Error creating breed chart: {str(e)}")
            return error_fig, visible

    # ----------------------------------------------------------------------------------------------------
    # Gender Chart
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        [
            Output("gender-chart", "figure"),
            Output("gender-chart", "style"),
        ],
        Input("chart-load-trigger", "data"),
        State("db-connection-state", "data"),
    )
    @CacheManager.memoize()
    def update_gender_chart(_, db_state: dict) -> tuple[Figure, dict]:
        """
        Update gender distribution chart using direct database queries

        This callback generates a pie chart visualizing the gender distribution
        of cats in the database.

        Args:
            _ (dict): Trigger from the chart load trigger event (not used directly)
            db_state (dict): Dictionary containing database connection state

        Returns:
            tuple[Figure, dict]: Tuple containing the Plotly figure and a style dictionary
        """
        visible = {"display": "block"}

        if not db_state.get("healthy", False):
            error_fig = create_error_figure("Database connection error - No data available")
            return error_fig, visible

        try:
            gender_data = db.get_gender_distribution()
            gender_df = process_gender_distribution(gender_data)
            chart = create_gender_pie_chart(gender_df)
            return chart, visible
        except Exception as e:
            logger.error(f"Error loading gender chart: {e}")
            error_fig = create_error_figure(f"Error loading gender data: {str(e)}")
            return error_fig, visible

    # ----------------------------------------------------------------------------------------------------
    # Birth Year Chart
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        [
            Output("birth-year-chart", "figure"),
            Output("birth-year-chart", "style"),
        ],
        Input("chart-load-trigger", "data"),
        State("db-connection-state", "data"),
    )
    def update_birth_year_chart(_, db_state: dict):
        """
        Update birth year distribution chart using direct database queries

        This callback generates a line chart visualizing the birth year distribution
        of cats in the database.

        Args:
            _ (dict): Trigger from the chart load trigger event (not used directly)
            db_state (dict): Dictionary containing database connection state

        Returns:
            tuple: Tuple containing (Plotly figure, style dictionary)
        """

        visible = {"display": "block"}

        if not db_state or not db_state.get("healthy", False):
            error_fig = create_error_figure("Database connection error - No data available")
            return error_fig, visible

        try:
            birth_year_data = db.get_birth_year_distribution()
            birth_year_df = process_birth_year_distribution(birth_year_data)

            chart = create_birth_year_line_chart(birth_year_df)

            return chart, visible

        except Exception as e:
            # Handle errors
            logger.error(f"Error loading birth year chart: {e}")
            error_fig = create_error_figure(f"Error loading birth year data: {str(e)}")
            return error_fig, visible

    # ----------------------------------------------------------------------------------------------------
    # Country Map
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        Output("country-map", "figure"),
        Input("chart-load-trigger", "data"),
        State("db-connection-state", "data"),
    )
    @CacheManager.memoize()
    def update_country_map(_, db_state: dict) -> Figure:
        """
        Update country distribution choropleth map using direct database queries

        This callback generates a choropleth map visualizing the geographical distribution
        of cats across countries in the database.

        Args:
            _ (dict): Trigger from the chart load trigger event (not used directly)
            db_state (dict): Dictionary containing database connection state

        Returns:
            Figure: A Plotly figure Figure containing the choropleth map
        """

        if not db_state.get("healthy", False):
            return create_error_figure("Database connection error - No data available")

        try:
            country_data = db.get_country_distribution()
            country_df = process_country_distribution(country_data)
            return create_country_map(country_df)
        except Exception as e:
            logger.error(f"Error loading country map: {e}")
            return create_error_figure(f"Error loading country data: {str(e)}")
