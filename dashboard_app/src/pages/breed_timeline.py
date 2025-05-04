import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, register_page

from dashboard_app.src.components.reusable.BasicCard import BasicCard
from dashboard_app.src.components.reusable.GraphCard import GraphCard
from dashboard_app.src.constants import colors

register_page(__name__, path="/breed-timeline", title="Breed Timeline")

SECTION_STYLE = {
    "margin-bottom": "1.5rem",
}

layout = html.Div(
    [
        dbc.Row(
            [
                # --------------------------------------------------
                # Left column for filters
                # --------------------------------------------------
                dbc.Col(
                    html.Div(
                        children=[
                            BasicCard(
                                title="Filters",
                                children=[
                                    # --------------------------------------------------
                                    # Year range filter
                                    # --------------------------------------------------
                                    html.Div(
                                        [
                                            html.Label(
                                                "Year Range:",
                                                className="fw-bold mb-1",
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        dbc.InputGroup(
                                                            [
                                                                dbc.InputGroupText("From"),
                                                                dbc.Input(
                                                                    id="year-start-input",
                                                                    type="number",
                                                                    min=0,
                                                                    max=0,
                                                                    step=1,
                                                                    value=0,
                                                                    disabled=True,
                                                                ),
                                                            ],
                                                            size="md",
                                                        ),
                                                    ),
                                                    dbc.Col(
                                                        dbc.InputGroup(
                                                            [
                                                                dbc.InputGroupText("To"),
                                                                dbc.Input(
                                                                    id="year-end-input",
                                                                    type="number",
                                                                    min=0,
                                                                    max=0,
                                                                    step=1,
                                                                    value=0,
                                                                    disabled=True,
                                                                ),
                                                            ],
                                                            size="md",
                                                        ),
                                                    ),
                                                ],
                                                className="g-2",
                                            ),
                                            # --------------------------------------------------
                                            # Loading indicator
                                            # --------------------------------------------------
                                            html.Div(
                                                [
                                                    html.I(className="fas fa-spinner fa-spin me-2"),
                                                    "Loading year range...",
                                                ],
                                                id="year-range-loading-indicator",
                                                className="text-muted mt-2 small fst-italic",
                                            ),
                                        ],
                                        style=SECTION_STYLE,
                                    ),
                                    # --------------------------------------------------
                                    # Breed selection
                                    # --------------------------------------------------
                                    html.Div(
                                        [
                                            html.Label(
                                                "Selected Breeds:",
                                                className="fw-bold mb-1",
                                            ),
                                            html.Div(
                                                dbc.Button(
                                                    "Add Breed",
                                                    id="open-breed-select-modal",
                                                    color="primary",
                                                    size="sm",
                                                    className="mb-2",
                                                ),
                                            ),
                                            html.Div(
                                                id="selected-breeds-badges",
                                                children=[
                                                    html.Div(
                                                        "No breeds selected", className="text-muted fst-italic"
                                                    )
                                                ],
                                                style={"max-height": "200px", "overflow-y": "auto"},
                                                className="p-2 border rounded",
                                            ),
                                        ],
                                        style=SECTION_STYLE,
                                    ),
                                    # --------------------------------------------------
                                    # Update Chart button
                                    # --------------------------------------------------
                                    dbc.Button(
                                        [html.I(className="fas fa-chart-line me-2"), "Generate Chart"],
                                        id="update-timeline-button",
                                        size="md",
                                        className="w-100",
                                        style={
                                            "background-color": colors.PRIMARY,
                                            "border": "0",
                                        },
                                    ),
                                ],
                            ),
                        ],
                    ),
                    sm=12,
                    md=3,
                ),
                # --------------------------------------------------
                # Right column for visualization
                # --------------------------------------------------
                dbc.Col(
                    [
                        GraphCard(
                            title="Breed Population Timeline",
                            children=[
                                dcc.Graph(
                                    id="breed-timeline-chart",
                                    figure=go.Figure(),
                                    config={
                                        "displayModeBar": True,
                                        "responsive": True,
                                        "toImageButtonOptions": {
                                            "format": "png",
                                            "filename": "breed_timeline",
                                            "scale": 2,
                                        },
                                    },
                                    style={"height": "100%", "display": "none"},
                                ),
                                html.Div(
                                    id="breed-timeline-info",
                                    className="mt-3 text-center",
                                ),
                            ],
                            card_body_class_name="px-0 py-0",
                            card_class_name="h-100",
                            card_body_style={
                                "min-height": "550px",
                                "padding": "0",
                                "align-content": "center",
                            },
                            loading_parent_style={
                                "height": "100%",
                                "align-content": "center",
                            },
                        ),
                    ],
                    sm=12,
                    md=9,
                ),
            ],
            className="g-3",
            style={"min-height": "85vh"},
        ),
        # --------------------------------------------------
        # Breed selection modal
        # --------------------------------------------------
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Select Breeds")),
                dbc.ModalBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Sort By:", className="fw-bold"),
                                        dbc.RadioItems(
                                            id="breed-sort-type",
                                            options=[
                                                {"label": "Most Common", "value": "count"},
                                                {"label": "Alphabetical", "value": "name"},
                                            ],
                                            value="count",
                                            inline=True,
                                            className="mb-3",
                                        ),
                                    ]
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        [html.I(className="fas fa-times-circle me-1"), "Reset Selection"],
                                        id="reset-breed-selection",
                                        color="secondary",
                                        size="sm",
                                        className="float-end",
                                    ),
                                ),
                            ],
                            className="mb-3",
                        ),
                        # --------------------------------------------------
                        # Search box with icon
                        # --------------------------------------------------
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText(html.I(className="fas fa-search")),
                                dbc.Input(
                                    id="breed-search-input",
                                    type="text",
                                    placeholder="Search breeds...",
                                    className="mb-0",
                                ),
                            ],
                            className="mb-2",
                        ),
                        # --------------------------------------------------
                        # Breed checklist with scrollable container
                        # --------------------------------------------------
                        html.Div(
                            dbc.Checklist(
                                id="breed-selector-checklist",
                                options=[],
                                value=[],
                                className="breed-selector-checklist",
                            ),
                            style={"max-height": "350px", "overflow-y": "auto"},
                            className="border rounded p-3",
                        ),
                    ]
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button(
                            [html.I(className="fas fa-times me-1"), "Close"],
                            id="close-breed-select-modal",
                            className="ms-auto",
                            color="secondary",
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-check me-1"), "Apply"],
                            id="apply-breed-selection",
                            color="primary",
                        ),
                    ]
                ),
            ],
            id="breed-select-modal",
            size="lg",
            is_open=False,
            scrollable=True,
        ),
        dcc.Store(id="selected-breeds-store", data=[]),
        dcc.Store(id="breed-timeline-load-trigger", data={"reload": True}),
        dcc.Store(id="year-range-sync", data={"value": [1990, 2023]}),
        dcc.Store(id="breed-search-store", data={"timeout_id": None}),
    ],
)

# ----------------------------------------------------------------------------------------------------
# Client-side callback to filter breeds based on search input
# ----------------------------------------------------------------------------------------------------
clientside_callback = """
function(search_value, all_options) {
    if (typeof window.breedSearchTimeout === 'undefined') {
        window.breedSearchTimeout = null;
    }
    
    if (window.breedSearchTimeout) {
        clearTimeout(window.breedSearchTimeout);
    }
    
    window.breedSearchTimeout = setTimeout(() => {
        if (!search_value) {
            Array.from(document.querySelectorAll('#breed-selector-checklist .form-check')).forEach(el => {
                el.style.display = 'block';
            });
            return;
        }
        
        const searchLower = search_value.toLowerCase();
        
        Array.from(document.querySelectorAll('#breed-selector-checklist .form-check')).forEach(el => {
            const text = el.textContent.toLowerCase();
            if (text.includes(searchLower)) {
                el.style.display = 'block';
            } else {
                el.style.display = 'none';
            }
        });
    }, 100);
}
"""

dash.clientside_callback(
    clientside_callback,
    [dash.Input("breed-search-input", "value")],
    [dash.State("breed-selector-checklist", "options")],
)
