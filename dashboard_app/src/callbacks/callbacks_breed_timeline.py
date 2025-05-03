import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, callback_context, html

from dashboard_app.src.constants import colors
from dashboard_app.src.data.db_connector import Neo4jConnector
from dashboard_app.src.utils.cache import CacheManager
from dashboard_app.src.utils.callback_utils import create_error_figure
from dashboard_app.src.utils.data_processing import process_breed_timeline_data
from dashboard_app.src.utils.logger import logger
from dashboard_app.src.utils.visualization import create_breed_timeline_chart

db = Neo4jConnector()


@CacheManager.memoize()
def _get_all_breeds():
    """
    Get a list of all available breeds from the database.

    Returns:
        pd.DataFrame: DataFrame containing breed codes and counts
    """

    breed_data = db.get_breed_distribution()

    if not breed_data:
        return pd.DataFrame(columns=["breed", "count"])

    df = pd.DataFrame([(record["breed"], record["count"]) for record in breed_data], columns=["breed", "count"])
    return df


@CacheManager.memoize()
def _get_birth_year_range():
    """
    Get the minimum and maximum birth years from the database.

    Returns:
        tuple: (min_year, max_year) containing the minimum and maximum birth years
    """
    try:
        result = db.get_birth_year_range()

        if not result:
            return 1980, 2023

        min_year = result[0]["min_year"]
        max_year = result[0]["max_year"]

        if min_year is None or max_year is None:
            return 1980, 2023

        return int(min_year), int(max_year)
    except Exception as e:
        logger.error(f"Error getting birth year range: {e}")
        return 1980, 2023


def register_callbacks(app):
    """
    Register all callbacks for the breed timeline page.

    Args:
        app: The Dash application instance
    """

    # ----------------------------------------------------------------------------------------------------
    # Initialize year input fields with min/max values from database
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        [
            Output("year-start-input", "min"),
            Output("year-start-input", "max"),
            Output("year-start-input", "value"),
            Output("year-start-input", "disabled"),
            Output("year-end-input", "min"),
            Output("year-end-input", "max"),
            Output("year-end-input", "value"),
            Output("year-end-input", "disabled"),
            Output("year-range-loading-indicator", "style"),
        ],
        [Input("breed-timeline-load-trigger", "data")],
        [State("db-connection-state", "data")],
    )
    def initialize_year_inputs(_, db_state):
        """
        Initialize year input fields with min/max values from database.

        Args:
            _: Trigger input (not used)
            db_state (dict): Database connection state

        Returns:
            tuple: Values for year input properties including min, max, value, disabled state
                  and loading indicator visibility
        """
        default_min_year = 1980
        default_max_year = 2023
        default_start = 1990
        default_end = 2023
        disabled = True
        show_loading = {"display": "block"}
        hide_loading = {"display": "none"}

        if not db_state.get("healthy", False):
            return (
                default_min_year,
                default_max_year,
                default_start,
                disabled,
                default_min_year,
                default_max_year,
                default_end,
                disabled,
                show_loading,
            )

        try:
            min_year, max_year = _get_birth_year_range()

            start_value = min_year
            end_value = max_year

            disabled = False

            return min_year, max_year, start_value, disabled, min_year, max_year, end_value, disabled, hide_loading
        except Exception as e:
            logger.error(f"Error initializing year inputs: {e}")
            return (
                default_min_year,
                default_max_year,
                default_start,
                True,
                default_min_year,
                default_max_year,
                default_end,
                True,
                show_loading,
            )

    # ----------------------------------------------------------------------------------------------------
    # Breed selection modal callbacks
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        Output("breed-select-modal", "is_open"),
        [
            Input("open-breed-select-modal", "n_clicks"),
            Input("close-breed-select-modal", "n_clicks"),
            Input("apply-breed-selection", "n_clicks"),
        ],
        State("breed-select-modal", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_breed_modal(open_clicks, close_clicks, apply_clicks, is_open):
        """
        Toggle the breed selection modal visibility based on user actions.
        """
        ctx = callback_context
        if not ctx.triggered:
            return is_open

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "open-breed-select-modal" and not is_open:
            return True
        elif (button_id == "close-breed-select-modal" or button_id == "apply-breed-selection") and is_open:
            return False
        else:
            return is_open

    # ----------------------------------------------------------------------------------------------------
    # Populate breed selector checklist with available breeds
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        Output("breed-selector-checklist", "options"),
        [
            Input("breed-timeline-load-trigger", "data"),
            Input("breed-sort-type", "value"),
        ],
    )
    def populate_breed_selector(_, sort_type):
        """
        Populate the breed selector checklist with available breeds.

        Args:
            _: Trigger input (not used)
            sort_type (str): How to sort breeds - 'count' or 'name'

        Returns:
            list: List of options for the breed selector checklist
        """
        try:
            breeds_df = _get_all_breeds()

            if breeds_df.empty:
                return []

            if sort_type == "name":
                breeds_df = breeds_df.sort_values("breed")
            else:
                breeds_df = breeds_df.sort_values("count", ascending=False)

            options = [
                {"label": f"{row['breed']} ({row['count']} cats)", "value": row["breed"]}
                for _, row in breeds_df.iterrows()
            ]

            return options

        except Exception as e:
            logger.error(f"Error populating breed selector: {e}")
            return []

    # ----------------------------------------------------------------------------------------------------
    # Reset breed selection
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        Output("breed-selector-checklist", "value"),
        Input("reset-breed-selection", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_breed_selection(_):
        """Reset the breed selection to empty"""
        return []

    # ----------------------------------------------------------------------------------------------------
    # Save selected breeds to store
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        Output("selected-breeds-store", "data"),
        Input("apply-breed-selection", "n_clicks"),
        State("breed-selector-checklist", "value"),
        prevent_initial_call=True,
    )
    def save_selected_breeds(_, selected_breeds):
        """Save the selected breeds to the store for use in visualizations"""
        return selected_breeds or []

    # ----------------------------------------------------------------------------------------------------
    # Update breed selection badges in the UI
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        Output("selected-breeds-badges", "children"),
        [Input("selected-breeds-store", "data")],
    )
    def update_selected_breeds_badges(selected_breeds):
        """
        Update the UI to show badges for each selected breed.

        Args:
            selected_breeds (list): List of selected breed codes

        Returns:
            list: List of badge components for the selected breeds
        """
        if not selected_breeds or len(selected_breeds) == 0:
            return [html.Div("No breeds selected", className="text-muted fst-italic")]

        badges = []
        for breed in selected_breeds:
            badges.append(
                dbc.Badge(
                    breed,
                    color=colors.ROSEWOOD,
                    className="me-1 mb-1",
                )
            )

        return badges

    # ----------------------------------------------------------------------------------------------------
    # Update breed timeline chart based on selected breeds and year range
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        [
            Output("breed-timeline-chart", "figure"),
            Output("breed-timeline-info", "children"),
            Output("breed-timeline-chart", "style"),
        ],
        [
            Input("update-timeline-button", "n_clicks"),
            Input("breed-timeline-load-trigger", "data"),
        ],
        [
            State("selected-breeds-store", "data"),
            State("year-start-input", "value"),
            State("year-end-input", "value"),
            State("db-connection-state", "data"),
        ],
    )
    def update_timeline_chart(n_clicks, load_trigger, selected_breeds, start_year, end_year, db_state):
        """
        Update the breed timeline chart based on selected breeds and year range.

        Args:
            n_clicks: Button click count (not used directly)
            load_trigger: Data load trigger
            selected_breeds (list): List of selected breed codes
            start_year (int): Start year from input field
            end_year (int): End year from input field
            db_state (dict): Database connection state

        Returns:
            tuple: (figure, chart_style, message_style)
                - figure: The Plotly figure object for the timeline chart
                - chart_style: CSS style dict for the chart
                - message_style: CSS style dict for the message div
        """

        hidden = {"display": "none"}
        visible = {"display": "block"}

        if n_clicks is None:
            return (
                go.Figure(),
                html.H5(
                    "Please select a breed and a year range to view the timeline.",
                    className="text-muted text-center my-3",
                ),
                hidden,
            )

        if not db_state.get("healthy", False):
            return (
                go.Figure(),
                html.H5("Database connection is not healthy", className="text-danger text-center my-3"),
                hidden,
            )

        if not selected_breeds or len(selected_breeds) == 0:
            return (
                go.Figure(),
                html.H5(
                    "Please select at least one breed to view the timeline.",
                    className="text-danger text-center my-3",
                ),
                hidden,
            )

        if start_year is None or end_year is None:
            return (
                go.Figure(),
                html.H5(
                    "Please select a valid year range.",
                    className="text-danger text-center my-3",
                ),
                hidden,
            )

        if start_year > end_year:
            return (
                go.Figure(),
                html.H5(
                    "Start year must be less than end year.",
                    className="text-danger text-center my-3",
                ),
                hidden,
            )

        min_year, max_year = _get_birth_year_range()
        if min_year is None or max_year is None:
            return (
                go.Figure(),
                html.H5(
                    "Error retrieving year range from database.",
                    className="text-danger text-center my-3",
                ),
                hidden,
            )
        elif start_year < min_year or end_year > max_year:
            return (
                go.Figure(),
                html.H5(
                    f"Year range must be between {min_year} and {max_year}.",
                    className="text-danger text-center my-3",
                ),
                hidden,
            )

        year_range = [start_year, end_year]

        try:
            breed_timeline_data = db.get_breed_timeline_data(
                selected_breeds=selected_breeds, year_range=year_range
            )

            if not breed_timeline_data:
                error_fig = create_error_figure("No data available for the selected breeds and year range")
                return error_fig, hidden

            df = process_breed_timeline_data(breed_timeline_data, year_range)

            figure = create_breed_timeline_chart(df, selected_breeds)

            return figure, "", visible

        except Exception as e:
            logger.error(f"Error creating breed timeline chart: {e}")
            return (
                go.Figure(),
                html.H5("Error creating chart. Please try again.", className="text-danger text-center my-3"),
                hidden,
            )
