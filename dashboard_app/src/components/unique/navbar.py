import dash
import dash_bootstrap_components as dbc
from dash import html

from dashboard_app.src.constants import colors


class MainNavbar(dbc.Navbar):
    """
    Navigation bar component for the dashboard.

    Provides links to all registered pages and responsive mobile functionality.
    """

    def __init__(self):
        """
        Initialize the MainNavbar component with links to all registered pages.
        """
        super().__init__(
            dbc.Container(
                [
                    # --------------------------------------------------
                    # Logo and title
                    # --------------------------------------------------
                    dbc.NavbarBrand(
                        html.H3(
                            "Cat Database Dashboard",
                            style={"color": colors.TEXT_SECONDARY, "margin-bottom": 0},
                        ),
                        href="/",
                    ),
                    # --------------------------------------------------
                    # Navbar toggler for mobile view
                    # --------------------------------------------------
                    dbc.NavbarToggler(id="navbar-toggler"),
                    dbc.Collapse(
                        dbc.Nav(
                            children=[
                                dbc.NavItem(
                                    dbc.NavLink(
                                        page["name"],
                                        href=page["path"],
                                        active="exact",
                                        style={
                                            "color": colors.TEXT_SECONDARY,
                                            "margin-right": "4px",
                                            "margin-left": "4px",
                                        },
                                        className="px-3",
                                    )
                                )
                                for page in dash.page_registry.values()
                                if page["path"] != "/"
                            ],
                            className="ms-auto",
                            navbar=True,
                            pills=True,
                        ),
                        id="navbar-collapse",
                        navbar=True,
                    ),
                ],
                fluid=True,
            ),
            color=colors.NAVBAR_BACKGROUND,
            dark=True,
            className="px-4",
            style={"height": "80px"},
        )
