import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyvis.network import Network

from dashboard_app.src.constants import colors


def create_breed_bar_chart(
    breed_df: pd.DataFrame = None,
    filter_type: str = "all",
    top_n: int = 10,
    min_count: int = 0,
    max_count: int = None,
    y_scale: str = "linear",
) -> go.Figure:
    """
    Create bar chart for breed distribution with filtering options.

    Args:
        breed_df (pd.DataFrame, optional): Pre-processed breed DataFrame. If None, will be fetched from DB
        filter_type (str): Type of filtering ('all', 'top', 'range')
        top_n (int): Number of top breeds to show when filter_type is 'top'
        min_count (int): Minimum count for range filtering
        max_count (int, optional): Maximum count for range filtering (None for no upper limit)
        y_scale (str): Y-axis scale ('linear' or 'log')

    Returns:
        go.Figure: Plotly figure object containing the breed bar chart
    """
    if breed_df.empty:
        return go.Figure()

    breed_df = breed_df.sort_values(by="count", ascending=False)

    if breed_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No breeds match the current filter criteria", height=600)
        return fig

    fig = px.bar(
        breed_df,
        x="breed",
        y="count",
        labels={
            "breed": "Breed code",
            "count": f"Number of cats ({y_scale} scale)" if y_scale == "log" else "Number of cats",
        },
        color="count",
        color_continuous_scale=colors.COLOR_CONTINUOUS_SCALE,
        log_y=(y_scale == "log"),
    )

    fig.update_traces(hovertemplate="<b>%{x}</b><br>Count: %{y:,}<extra></extra>")

    x_angle = -45 if len(breed_df) > 10 else 0

    fig.update_layout(
        xaxis=dict(
            tickangle=x_angle,
            tickmode="array" if len(breed_df) > 30 else None,
            tickvals=list(range(0, len(breed_df), max(1, len(breed_df) // 20))) if len(breed_df) > 30 else None,
        ),
        height=500,
        template="plotly_white",
        plot_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        paper_bgcolor=colors.CARD_BACKGROUND,
        font={"color": colors.TEXT_PRIMARY},
        margin=dict(t=10, b=10, l=10, r=10),
        hovermode="x unified",
    )

    return fig


def create_gender_pie_chart(gender_df: pd.DataFrame = None) -> go.Figure:
    """
    Create pie chart for gender distribution.

    Args:
        gender_df (pd.DataFrame, optional): Pre-processed gender DataFrame. If None, will be fetched from DB

    Returns:
        go.Figure: Plotly figure object containing the gender pie chart
    """
    if gender_df.empty:
        return go.Figure()

    fig = px.pie(
        gender_df,
        names="gender",
        values="count",
        color="gender",
        color_discrete_map={
            "male": colors.MALE_COLOR,
            "female": colors.FEMALE_COLOR,
            "unknown": colors.UNKNOWN_GENDER_COLOR,
        },
    )

    fig.update_traces(textinfo="percent+label", insidetextfont=dict(size=14), rotation=270)

    fig.update_layout(
        height=250,
        plot_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        paper_bgcolor=colors.CARD_BACKGROUND,
        font={"color": colors.TEXT_PRIMARY},
        margin=dict(t=10, b=10, l=10, r=10),
        autosize=True,
    )

    return fig


def create_birth_year_line_chart(birth_year_df: pd.DataFrame = None) -> go.Figure:
    """
    Create line chart for birth year distribution.

    Args:
        birth_year_df (pd.DataFrame, optional): Pre-processed birth year DataFrame. If None, will be fetched from DB

    Returns:
        go.Figure: Plotly figure object containing the birth year distribution line chart
    """

    if birth_year_df.empty:
        return go.Figure()

    fig = px.line(
        birth_year_df,
        x="birth_year",
        y="count",
        labels={"birth_year": "Birth year", "count": "Number of cats"},
        markers=True,
    )

    fig.update_traces(line=dict(color=colors.PRIMARY))

    year_range = birth_year_df["birth_year"].max() - birth_year_df["birth_year"].min()

    if year_range > 30:
        dtick = 5
    elif year_range > 15:
        dtick = 2
    else:
        dtick = 1

    fig.update_layout(
        xaxis=dict(
            tickmode="linear",
            tick0=birth_year_df["birth_year"].min(),
            dtick=dtick,
            tickangle=-45 if year_range > 10 else 0,
        ),
        height=250,
        template="plotly_white",
        plot_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        paper_bgcolor=colors.CARD_BACKGROUND,
        font={"color": colors.TEXT_PRIMARY},
        margin=dict(t=10, b=10, l=10, r=10),
        hovermode="x unified",
    )

    return fig


def create_country_map(country_df: pd.DataFrame = None) -> go.Figure:
    """
    Create choropleth map for country distribution.

    Args:
        country_df (pd.DataFrame, optional): Pre-processed country DataFrame. If None, will be fetched from DB

    Returns:
        go.Figure: Plotly figure object containing the country distribution choropleth map
    """
    if country_df.empty:
        return go.Figure()

    fig = px.choropleth(
        country_df,
        locations="country",
        locationmode="country names",
        color="count",
        hover_name="country",
        color_continuous_scale=colors.COLOR_CONTINUOUS_SCALE,
    )

    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type="equirectangular"),
        height=500,
        plot_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        paper_bgcolor=colors.CARD_BACKGROUND,
        font={"color": colors.TEXT_PRIMARY},
        margin=dict(t=10, b=10, l=10, r=10),
    )

    return fig


def create_family_tree_network(
    depth: int,
    graph_structure_data: dict,
    root_cat_id: str,
    inbreeding_coefficient: float | None,
    root_cat_legend_data: dict,
) -> str:
    """
    Generate an interactive family tree network visualization using Pyvis.

    Args:
        depth (int): Maximum depth of the tree.
        graph_structure_data (dict): Dictionary containing 'nodes' (list of detailed cat dicts)
                                     and 'edges' (list of relationship dicts).
        root_cat_id (str): ID of the root cat.
        inbreeding_coefficient (float | None): Calculated inbreeding coefficient for the root cat.
        root_cat_legend_data (dict): Detailed dictionary for the root cat for legend display.

    Returns:
        str: HTML content of the generated Pyvis network visualization.
    """
    if not graph_structure_data or not graph_structure_data.get("nodes"):
        net = Network(height="600px", width="100%", directed=True)
        return net.generate_html()

    G = nx.DiGraph()

    for cat_details in graph_structure_data.get("nodes", []):
        cat_id = cat_details.get("id")
        if not cat_id:
            continue

        name = cat_details.get("name", "Unknown")
        gender = cat_details.get("gender", "unknown")

        tooltip = _format_cat_details_for_tooltip(cat_details)

        if gender == "male":
            node_color = colors.MALE_COLOR
        elif gender == "female":
            node_color = colors.FEMALE_COLOR
        else:
            node_color = colors.UNKNOWN_GENDER_COLOR

        G.add_node(
            cat_id,
            label=name,
            title=tooltip,
            color=node_color,
            gender=gender,
        )

    for edge in graph_structure_data.get("edges", []):
        child_id = edge.get("child_id")
        parent_id = edge.get("parent_id")
        rel_type = edge.get("rel_type")

        if child_id and parent_id:
            G.add_edge(parent_id, child_id, label=rel_type, title=rel_type)

    net = Network(
        height="100%", width="100%", directed=True, notebook=False, select_menu=True, cdn_resources="remote"
    )

    depth_scale_multiplier = min(depth, 20)

    root_node_size = 30 + 2 * depth_scale_multiplier
    node_label_size = 14 + 2 * depth_scale_multiplier
    edge_selection_width = 0.5 + depth_scale_multiplier * 0.5
    edge_hover_width = 0.5 + depth_scale_multiplier * 0.5
    gravitational_constant = -30 - 5 * depth_scale_multiplier
    central_gravity = max(0.01 - 0.001 * depth_scale_multiplier, 0.001)

    net.options = {
        "nodes": {
            "font": {"size": node_label_size, "color": colors.TEXT_PRIMARY},
        },
        "edges": {
            "font": {"size": 0},
            "smooth": {"type": "dynamic"},
            "selectionWidth": edge_selection_width,
            "hoverWidth": edge_hover_width,
        },
        "physics": {
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
                "gravitationalConstant": gravitational_constant,
                "centralGravity": central_gravity,
            },
            "stabilization": {
                "enabled": True,
                "iterations": 5000,
                "updateInterval": 100,
            },
        },
        "interaction": {
            "hover": True,
            "tooltipDelay": 100,
        },
    }

    for node_id, node_data in G.nodes(data=True):
        is_root_cat = str(node_id) == str(root_cat_id)
        node_size = root_node_size if is_root_cat else 20
        border_width = 4 if is_root_cat else 2
        shape = "star" if is_root_cat else "dot"

        net.add_node(
            node_id,
            label=node_data.get("label", node_id),
            title=node_data.get("title", ""),
            color=node_data.get("color", colors.PRIMARY),
            shape=shape,
            size=node_size,
            borderWidth=border_width,
            borderWidthSelected=6,
        )

    for start, end, data in G.edges(data=True):
        net.add_edge(
            start,
            end,
            label=data.get("label", ""),
            title=data.get("title", ""),
            arrows={"from": {"enabled": True}},
        )

    html_content = net.generate_html()
    html_content = add_custom_js(html_content)
    html_content = add_custom_legend(html_content, root_cat_id, inbreeding_coefficient, root_cat_legend_data)
    html_content = add_custom_css(html_content)

    return html_content


def add_custom_js(html_content: str) -> str:
    """
    Add custom JavaScript.

    Fixes the issue where clicking on an empty space in the network resets the selection.

    Adds a button to toggle the physics simulation on and off.

    Args:
        html_content (str): HTML content for the network visualization

    Returns:
        str: Updated HTML content with the reset selection fix
    """
    reset_selection_js = """
    <script>
    window.addEventListener('load', function() {
        try {
            if (typeof network !== 'undefined') {
                network.on("click", function(params) {
                    if (params.nodes.length === 0 && params.edges.length === 0) {
                        neighbourhoodHighlight({nodes: []});
                    }
                });
                
                var physicsButton = document.createElement('button');
                physicsButton.id = 'physics-toggle-btn';
                physicsButton.innerHTML = '⏸️ Freeze Layout';
                physicsButton.title = 'Toggle physics simulation on/off';
                
                var physicsEnabled = true;
                
                physicsButton.addEventListener('click', function() {
                    physicsEnabled = !physicsEnabled;
                    
                    if (physicsEnabled) {
                        network.setOptions({ physics: { enabled: true } });
                        physicsButton.innerHTML = '⏸️ Freeze Layout';
                        physicsButton.classList.remove('active');
                    } else {
                        network.setOptions({ physics: { enabled: false } });
                        physicsButton.innerHTML = '▶️ Resume Layout';
                        physicsButton.classList.add('active');
                    }
                });
                
                document.body.appendChild(physicsButton);
            }
        } catch (e) {
            console.error("Error in network setup:", e);
        }
    });
    </script>
    """
    return html_content.replace("</body>", reset_selection_js + "</body>")


def add_custom_legend(html_content: str, cat_id: str, inbreeding_coefficient: float, cat_data: dict) -> str:
    """
    Add a custom legend to the network visualization with cat information.

    Args:
        html_content (str): HTML content for the network visualization
        cat_id (str): ID of the root cat to highlight in the visualization
        inbreeding_coefficient (float): Inbreeding coefficient to display in the visualization
        cat_data (dict): Flattened cat data dictionary with direct access to fields

    Returns:
        str: Updated HTML content with the custom legend
    """
    if cat_id and cat_data:
        cat_name = cat_data.get("name", "Unknown")
        cat_gender = cat_data.get("gender", "Unknown")
        date_of_birth = cat_data.get("date_of_birth", "Unknown")
        registration_number = cat_data.get("registration_number_current", "Unknown")

        breed_code = cat_data.get("breed_code", "Unknown")
        color_code = cat_data.get("color_code", "Unknown")
        color_definition = cat_data.get("color_definition", "Unknown")
        birth_country_name = cat_data.get("birth_country_name", "Unknown")
        current_country_name = cat_data.get("current_country_name", "Unknown")
        cattery_name = cat_data.get("cattery_name", "Unknown")
        source_db_name = cat_data.get("source_db_name", "Unknown")

        combined_code = ""
        if breed_code != "Unknown" and color_code != "Unknown":
            combined_code = f"{breed_code} {color_code}"

        title_before = cat_data.get("title_before", "")
        title_after = cat_data.get("title_after", "")
        titles = []
        if title_before and title_before != "unknown":
            titles.append(title_before)
        if title_after and title_after != "unknown":
            titles.append(title_after)
        titles_str = ", ".join(titles) if titles else "None"

        gender_icon = "♂️" if cat_gender == "male" else "♀️" if cat_gender == "female" else "⚥"
        gender_color = (
            colors.MALE_COLOR
            if cat_gender == "male"
            else colors.FEMALE_COLOR
            if cat_gender == "female"
            else colors.UNKNOWN_GENDER_COLOR
        )

        inbreeding_percentage = 0
        inbreeding_label = "N/A"
        inbreeding_color = "#28a745"

        if inbreeding_coefficient is not None:
            inbreeding_percentage = inbreeding_coefficient * 100
            inbreeding_label = f"{inbreeding_percentage:.3f}%"
            inbreeding_color = (
                "#dc3545" if inbreeding_percentage > 15 else "#ffc107" if inbreeding_percentage > 5 else "#28a745"
            )

        custom_legend = f"""
        <div class="cat-info-legend" 
            style="position: absolute; 
                    top: 20px; 
                    right: 20px; 
                    background-color: rgba(255, 255, 255, 0.95);
                    padding: 12px 15px; 
                    border-radius: 6px; 
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
                    max-width: 300px;
                    max-height: 80%;
                    overflow-y: auto;">
            
            <div style="font-weight: bold; 
                        margin-bottom: 8px; 
                        font-size: 16px; 
                        border-bottom: 1px solid #ddd; 
                        padding-bottom: 5px;">
                <span style="color: {gender_color};">{gender_icon}</span> {cat_name}
            </div>
            
            <div style="font-size: 13px;">
                <div><strong>ID:</strong> {cat_id}</div>
                <div><strong>Date of Birth:</strong> {date_of_birth}</div>
                <div><strong>Gender:</strong> {cat_gender.capitalize() if cat_gender else "Unknown"}</div>
                {f"<div><strong>Registration:</strong> {registration_number}</div>" if registration_number != "Unknown" else ""}
                {f"<div><strong>Titles:</strong> {titles_str}</div>" if titles_str != "None" else ""}
                {f"<div><strong>Breed:</strong> {breed_code}</div>" if breed_code != "Unknown" else ""}
                {f"<div><strong>Color:</strong> {color_code}</div>" if color_code != "Unknown" else ""}
                {f"<div><strong>Combined:</strong> {combined_code}</div>" if combined_code else ""}
                {f"<div><strong>Color Definition:</strong> {color_definition}</div>" if color_definition != "Unknown" else ""}
                {f"<div><strong>Birth Country:</strong> {birth_country_name}</div>" if birth_country_name != "Unknown" else ""}
                {f"<div><strong>Current Country:</strong> {current_country_name}</div>" if current_country_name != "Unknown" and current_country_name != birth_country_name else ""}
                {f"<div><strong>Cattery:</strong> {cattery_name}</div>" if cattery_name != "Unknown" else ""}
                {f"<div><strong>Database Source:</strong> {source_db_name}</div>" if source_db_name != "Unknown" else ""}
                <div><strong>Inbreeding Coefficient:</strong> <span style="color: {inbreeding_color}; font-weight: bold;">{inbreeding_label}</span></div>
            </div>
        </div>

        <div class="legend-wrapper" 
            style="position: absolute; 
                    top: 20px; 
                    left: 20px; 
                    background-color: rgba(255, 255, 255, 0.95);
                    padding: 8px; 
                    border-radius: 4px; 
                    font-size: 12px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);">
                    
            <div style="margin-bottom: 5px; font-weight: bold;">
                Gender legend:
            </div>
            
            <div style="display: flex; 
                        align-items: center; 
                        margin-bottom: 3px;">
                <div style="width: 12px; 
                            height: 12px; 
                            background-color: {colors.MALE_COLOR}; 
                            border-radius: 50%; 
                            margin-right: 5px;">
                </div>
                <span>Male</span>
            </div>
            
            <div style="display: flex; 
                        align-items: center; 
                        margin-bottom: 3px;">
                <div style="width: 12px; 
                            height: 12px; 
                            background-color: {colors.FEMALE_COLOR}; 
                            border-radius: 50%; 
                            margin-right: 5px;">
                </div>
                <span>Female</span>
            </div>
            
            <div style="display: flex; 
                        align-items: center;">
                <div style="width: 12px; 
                            height: 12px; 
                            background-color: {colors.UNKNOWN_GENDER_COLOR}; 
                            border-radius: 50%; 
                            margin-right: 5px;">
                </div>
                <span>Unknown</span>
            </div>
        </div>
        """
        return html_content.replace("</body>", f"{custom_legend}</body>")

    return html_content


def add_custom_css(html_content: str) -> str:
    """
    Add custom CSS to the HTML content for styling.

    Args:
        html_content (str): HTML content for the network visualization

    Returns:
        str: Updated HTML content with custom CSS
    """
    custom_css = """
    <style>
        html, body {
            overflow: hidden;
            height: 100%;
        }
        .card {
            border: none;
            height: 100%;
        }
        #mynetwork {
            border: none;
            padding: 0;
            margin: 0;
        }
        .cat-info-legend {
            transition: opacity 0.3s ease;
        }
        .cat-info-legend:hover {
            opacity: 1 !important;
        }
        
        #select-menu {
            display:none
        }
        
        #physics-toggle-btn {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background-color: rgba(255, 255, 255, 0.95);
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 14px;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            transition: all 0.2s ease;
        }
        
        #physics-toggle-btn:hover {
            background-color: #f8f8f8;
            box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
        }
        
        #physics-toggle-btn.active {
            background-color: #e6f7ff;
            border-color: #1890ff;
            color: #1890ff;
        }
    </style>
    """

    return html_content.replace("</head>", custom_css + "</head>")


def create_breed_density_map(breed_density_df: pd.DataFrame, selected_breed: str) -> go.Figure:
    """
    Create choropleth map showing density of specific breeds by region.

    Args:
        breed_density_df (pd.DataFrame): Pre-processed breed density DataFrame for the selected breed
        selected_breed (str): Selected breed to display in the map

    Returns:
        go.Figure: Plotly figure object containing the breed density choropleth map
    """
    if breed_density_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title={
                "text": f"No distribution data available for breed: {selected_breed}",
                "y": 0.5,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "middle",
                "font": {"size": 18, "color": "#666666"},
            },
            height=550,
            plot_bgcolor=colors.PLOT_BACKGROUND_COLOR,
            paper_bgcolor=colors.CARD_BACKGROUND,
            font={"color": colors.TEXT_PRIMARY},
        )
        return fig

    fig = px.choropleth(
        breed_density_df,
        locations="country",
        locationmode="country names",
        color="density",
        hover_name="country",
        hover_data={"breed_count": ":.0f", "total_cats": ":.0f", "density": ":.2f"},
        labels={
            "density": "Breed density (%)",
            "breed_count": "Cat count for breed",
            "total_cats": "Total cats in country",
        },
        color_continuous_scale="peach",
    )

    fig.add_annotation(
        x=0.5,
        y=1.05,
        xref="paper",
        yref="paper",
        text=f"Breed: {selected_breed}",
        showarrow=False,
        font=dict(family="Arial", size=16, color=colors.TEXT_PRIMARY),
        align="center",
        bgcolor=colors.CARD_BACKGROUND,
        opacity=0.8,
    )

    fig.update_layout(
        coloraxis_colorbar=dict(title="% of population", ticksuffix="%"),
        geo=dict(showframe=False, showcoastlines=True, projection_type="equirectangular"),
        height=550,
        plot_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        paper_bgcolor=colors.CARD_BACKGROUND,
        font={"color": colors.TEXT_PRIMARY},
        margin=dict(b=0, l=0, r=0),
    )

    return fig


def create_breed_timeline_chart(breed_year_df: pd.DataFrame = None, selected_breeds: list = None) -> go.Figure:
    """
    Create line chart for breed population over time.

    Args:
        breed_year_df (pd.DataFrame): DataFrame containing breed count by year data
        selected_breeds (list): List of selected breed codes to include in the chart

    Returns:
        go.Figure: Plotly figure object containing the breed timeline chart
    """

    if breed_year_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No data available for the selected breeds and time period", height=500)
        return fig

    if selected_breeds:
        breed_year_df = breed_year_df[breed_year_df["breed"].isin(selected_breeds)]

    if breed_year_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No data available for the selected breeds and time period", height=500)
        return fig

    fig = go.Figure()

    for i, breed in enumerate(selected_breeds):
        breed_data = breed_year_df[breed_year_df["breed"] == breed]

        if not breed_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=breed_data["year"],
                    y=breed_data["count"],
                    mode="lines+markers",
                    name=breed,
                )
            )

    if not breed_year_df.empty:
        year_min = breed_year_df["year"].min()
        year_max = breed_year_df["year"].max()
        year_range = year_max - year_min

        if year_range > 40:
            dtick = 5
        elif year_range > 15:
            dtick = 2
        else:
            dtick = 1
    else:
        dtick = 5

    fig.update_layout(
        xaxis=dict(
            title="Year",
            tickmode="linear",
            dtick=dtick,
            tickangle=-45 if year_range > 10 else 0,
        ),
        yaxis=dict(
            title="Number of cats",
        ),
        height=550,
        template="plotly_white",
        plot_bgcolor=colors.PLOT_BACKGROUND_COLOR,
        paper_bgcolor=colors.CARD_BACKGROUND,
        font={"color": colors.TEXT_PRIMARY},
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor=colors.CARD_BACKGROUND,
            bordercolor=colors.BORDER_COLOR,
        ),
    )

    return fig


def _format_cat_details_for_tooltip(cat_details: dict) -> str:
    """
    Format cat details for tooltips in a way that pyvis can display properly.
    Pyvis doesn't render HTML tags but displays them as-is, so we need to use
    plain text with newlines instead.

    Args:
        cat_details (dict): Flattened cat details dict with direct access to fields

    Returns:
        str: Formatted string for tooltip with proper line breaks
    """
    cat_id = cat_details.get("id", "Unknown")
    name = cat_details.get("name", "Unknown")
    gender = cat_details.get("gender", "Unknown")
    date_of_birth = cat_details.get("date_of_birth", "Unknown")
    registration_number = cat_details.get("registration_number_current", "Unknown")

    tooltip = f"{name} (ID: {cat_id})\n"
    tooltip += f"Gender: {gender.capitalize() if gender else 'Unknown'}\n"
    tooltip += f"Date of birth: {date_of_birth}"

    if registration_number and registration_number != "Unknown":
        tooltip += f"\nRegistration: {registration_number}"

    title_before = cat_details.get("title_before", "")
    title_after = cat_details.get("title_after", "")
    titles = []
    if title_before and title_before != "unknown":
        titles.append(title_before)
    if title_after and title_after != "unknown":
        titles.append(title_after)
    if titles:
        tooltip += f"\nTitles: {', '.join(titles)}"

    chip = cat_details.get("chip", "")
    if chip and chip != "unknown":
        tooltip += f"\nChip: {chip}"

    breed_code = cat_details.get("breed_code")
    if breed_code:
        tooltip += f"\nBreed: {breed_code}"

    breed_full_name = cat_details.get("breed_full_name")
    if breed_full_name:
        tooltip += f"\nBreed name: {breed_full_name}"

    color_code = cat_details.get("color_code")
    if color_code:
        tooltip += f"\nColor: {color_code}"

    color_definition = cat_details.get("color_definition")
    if color_definition:
        tooltip += f"\nColor definition: {color_definition}"

    if breed_code and color_code:
        tooltip += f"\nCombined code: {breed_code} {color_code}"

    birth_country_name = cat_details.get("birth_country_name")
    if birth_country_name:
        tooltip += f"\nBirth country: {birth_country_name}"

    current_country_name = cat_details.get("current_country_name")
    if current_country_name and current_country_name != birth_country_name:
        tooltip += f"\nCurrent country: {current_country_name}"

    cattery_name = cat_details.get("cattery_name")
    if cattery_name:
        tooltip += f"\nCattery: {cattery_name}"

    source_db_name = cat_details.get("source_db_name")
    if source_db_name:
        tooltip += f"\nDatabase source: {source_db_name}"

    return tooltip
