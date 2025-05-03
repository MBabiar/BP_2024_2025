import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback_context, html
from dash.exceptions import PreventUpdate

from dashboard_app.src.callbacks.callbacks_database import db
from dashboard_app.src.constants import colors
from dashboard_app.src.utils.cache import CacheManager
from dashboard_app.src.utils.data_processing import process_family_tree_data
from dashboard_app.src.utils.inbreeding_coefficient import (
    calculate_inbreeding_coefficient_modern,
)
from dashboard_app.src.utils.logger import logger
from dashboard_app.src.utils.visualization import create_family_tree_network


def register_callbacks(app) -> None:
    """
    Register callbacks for family tree visualization functionality.

    Args:
        app: The Dash application instance to register callbacks with

    Returns:
        None
    """

    # ----------------------------------------------------------------------------------------------------
    # Search for cats by name or ID
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        [
            Output("cat-search-results", "children"),
            Output("cat-search-store", "data"),
        ],
        Input("cat-search-button", "n_clicks"),
        [
            State("cat-search-input", "value"),
            State("db-connection-state", "data"),
        ],
    )
    def search_cats(n_clicks: int, search_term: str, db_state: dict) -> tuple[html.Div, list]:
        """
        Search for cats by name or ID and display results.

        Args:
            n_clicks (int): Number of times the search button has been clicked
            search_term (str): The search term entered by the user
            db_state (dict): Current database connection state

        Returns:
            tuple: A tuple containing (search results UI component, search results data list)
        """
        if n_clicks is None or not search_term or not db_state.get("healthy", False):
            return html.Div(), []

        try:
            search_results = db.search_cats_by_name_or_id(search_term)

            if not search_results:
                return html.P("No cats found matching your search.", className="text-muted"), []

            result_items = []
            for cat in search_results:
                result_items.append(
                    dbc.Button(
                        f"{cat['name']} (ID: {cat['id']})",
                        id={"type": "search-result-btn", "index": cat["id"]},
                        color=None,
                        className="d-block mb-1",
                        style={
                            "backgroundColor": colors.WHITE,
                            "color": colors.TEXT_PRIMARY,
                            "border": f"1px solid {colors.BORDER_COLOR}",
                            "textAlign": "left",
                            "width": "100%",
                        },
                    )
                )

            return html.Div(result_items), search_results

        except Exception as e:
            logger.error(f"Error searching for cats: {e}")
            return html.P(f"Error: {str(e)}", className="text-danger"), []

    # ----------------------------------------------------------------------------------------------------
    # Select a cat from search results
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        [
            Output("selected-cat-store", "data"),
            Output("cat-selector", "value"),
            Output("selected-cat-info", "children"),
            Output({"type": "search-result-btn", "index": dash.ALL}, "style"),
        ],
        Input({"type": "search-result-btn", "index": dash.ALL}, "n_clicks"),
        [
            State({"type": "search-result-btn", "index": dash.ALL}, "id"),
            State("cat-search-store", "data"),
            State({"type": "search-result-btn", "index": dash.ALL}, "style"),
            State("db-connection-state", "data"),
        ],
        prevent_initial_call=True,
    )
    def select_searched_cat(
        n_clicks: list, btn_ids: list, search_results: list, current_styles: list, db_state: dict
    ) -> tuple:
        """
        Select a cat from search results and update the UI accordingly.

        Args:
            n_clicks (list): List of click counts for each search result button
            btn_ids (list): List of button IDs containing cat indices
            search_results (list): List of cat data from search results
            current_styles (list): Current styles for all search result buttons
            db_state (dict): Current database connection state

        Returns:
            tuple: A tuple containing (selected cat data, cat ID, cat info component, updated button styles)

        Raises:
            PreventUpdate: If no button was clicked or selected cat not found
        """
        ctx = callback_context
        if not ctx.triggered or not n_clicks:
            raise PreventUpdate

        try:
            trigger_id = ctx.triggered_id
            if not isinstance(trigger_id, dict) or trigger_id.get("type") != "search-result-btn":
                logger.warning(f"Unexpected trigger ID format: {trigger_id}")
                raise PreventUpdate

            cat_id = trigger_id.get("index")
            if cat_id is None:
                logger.warning(f"Could not extract cat ID from trigger ID: {trigger_id}")
                raise PreventUpdate

            selected_cat = None
            for cat in search_results:
                if str(cat["id"]) == str(cat_id):
                    selected_cat = cat
                    break

            if not selected_cat:
                raise PreventUpdate

            gender = selected_cat.get("gender", "")
            gender_icon = "♂️" if gender == "male" else "♀️" if gender == "female" else "⚥"
            gender_color = (
                colors.MALE_COLOR
                if gender == "male"
                else colors.FEMALE_COLOR
                if gender == "female"
                else colors.UNKNOWN_GENDER_COLOR
            )

            cat_info = html.Div(
                [
                    html.H5(
                        [
                            html.Span(f"{gender_icon} ", style={"color": gender_color}),
                            f"{selected_cat['name']} (ID: {selected_cat['id']})",
                        ],
                        className="m-0",
                    ),
                    html.P(
                        f"Date of birth: {selected_cat.get('date_of_birth', 'Unknown')}",
                        className="text-muted small m-0",
                    ),
                ]
            )

            new_btn_styles = []
            for button_id in btn_ids:
                if str(button_id["index"]) == str(cat_id):
                    new_btn_styles.append(
                        {
                            "backgroundColor": colors.GRAY_1,
                            "color": colors.TEXT_PRIMARY,
                            "border": f"1px solid {colors.BORDER_COLOR}",
                            "textAlign": "left",
                            "width": "100%",
                        }
                    )
                else:
                    new_btn_styles.append(
                        {
                            "backgroundColor": colors.WHITE,
                            "color": colors.TEXT_PRIMARY,
                            "border": f"1px solid {colors.BORDER_COLOR}",
                            "textAlign": "left",
                            "width": "100%",
                        }
                    )

            return selected_cat, cat_id, cat_info, new_btn_styles

        except Exception as e:
            logger.error(f"Error selecting cat: {e}")
            raise PreventUpdate

    # ----------------------------------------------------------------------------------------------------
    # Clear selection when a new search is performed
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        [
            Output("selected-cat-store", "data", allow_duplicate=True),
            Output("selected-cat-info", "children", allow_duplicate=True),
        ],
        Input("cat-search-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_selection_on_search(n_clicks: int) -> tuple[None, html.P]:
        """
        Clear the current cat selection when a new search is performed.

        Args:
            n_clicks (int): Number of times the search button has been clicked

        Returns:
            tuple: A tuple containing (None for data store, UI component showing no selection)

        Raises:
            PreventUpdate: If no button has been clicked
        """
        if n_clicks is None:
            raise PreventUpdate

        return None, html.P("No cat selected", className="text-muted m-0")

    # ----------------------------------------------------------------------------------------------------
    # Generate family tree for the selected cat
    # ----------------------------------------------------------------------------------------------------
    @app.callback(
        [
            Output("family-tree-graph", "srcDoc"),
            Output("family-tree-info", "children"),
            Output("family-tree-graph", "style"),
        ],
        Input("generate-tree-button", "n_clicks"),
        [
            State("selected-cat-store", "data"),
            State("tree-depth-input", "value"),
            State("db-connection-state", "data"),
        ],
    )
    @CacheManager.memoize(args_to_ignore=["n_clicks", "db_state"])
    def update_family_tree(
        n_clicks: int, selected_cat: dict, depth: int, db_state: dict
    ) -> tuple[str, object, dict]:
        """
        Generate and display family tree for the selected cat.
        Uses server-side caching with n_clicks excluded from the cache key.

        Args:
            n_clicks (int): Number of times the generate tree button has been clicked (excluded from cache key)
            selected_cat (dict): Data for the currently selected cat
            depth (int): Maximum number of generations to include in the family tree
            db_state (dict): Current database connection state (excluded from cache key)

        Returns:
            tuple: A tuple containing (HTML content for iframe, info/error message component,
                  iframe style dictionary)
        """

        default_iframe_style = {
            "width": "100%",
            "height": "100%",
            "border": "none",
            "padding": "0",
            "margin": "0",
            "overflow": "hidden",
        }
        hidden_iframe_style = {
            "width": "0",
            "height": "0",
            "border": "none",
            "display": "none",
        }

        if n_clicks is None:
            return (
                "",
                html.H5(
                    "Select a cat and click 'Generate Family Tree'",
                    className="text-muted text-center my-3",
                ),
                hidden_iframe_style,
            )

        if not selected_cat:
            return (
                "",
                html.H5("Please select a cat", className="text-center py-3 text-warning"),
                hidden_iframe_style,
            )

        if not db_state.get("healthy", False):
            return (
                "",
                html.Div(
                    [
                        html.Span("⚠️", style={"fontSize": "2rem"}),
                        html.H5("Database connection error", className="text-danger mt-2"),
                    ],
                    className="text-center",
                ),
                hidden_iframe_style,
            )

        cat_id = selected_cat["id"]

        try:
            raw_tree_data = db.get_cat_family_tree(cat_id, depth=depth)

            if not raw_tree_data:
                return (
                    "",
                    html.Div(
                        [
                            html.Span("⚠️", style={"fontSize": "1.5rem"}),
                            html.H5("No family data found for this cat", className="text-center py-2"),
                        ],
                        className="text-center",
                    ),
                    hidden_iframe_style,
                )

            graph_structure_data, root_cat_details = process_family_tree_data(raw_tree_data)

            try:
                inbreeding_coefficient = calculate_inbreeding_coefficient_modern(cat_id)
            except Exception as e:
                logger.warning(f"Could not calculate inbreeding coefficient for {cat_id}: {e}")
                inbreeding_coefficient = None

            html_content = create_family_tree_network(
                depth=depth,
                graph_structure_data=graph_structure_data,
                root_cat_id=cat_id,
                inbreeding_coefficient=inbreeding_coefficient,
                root_cat_legend_data=root_cat_details,
            )

            return html_content, "", default_iframe_style

        except Exception as e:
            logger.error(f"Error generating family tree: {e}")
            return (
                "",
                html.Div(
                    [
                        html.Span("⚠️", style={"fontSize": "1.5rem", "color": colors.DANGER}),
                        html.H5("Error generating family tree", className="text-danger text-center mt-2"),
                        html.P(f"Details: {str(e)}", className="text-center small"),
                    ],
                    className="text-center",
                ),
                hidden_iframe_style,
            )
