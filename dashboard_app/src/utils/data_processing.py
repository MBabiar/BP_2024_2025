import pandas as pd


def process_breed_distribution(breed_data: list) -> pd.DataFrame:
    """
    Process breed distribution data for visualization.

    Args:
        breed_data (list): Raw breed distribution data from database query

    Returns:
        pd.DataFrame: DataFrame with breed names and counts suitable for visualization
    """
    if not breed_data:
        return pd.DataFrame(columns=["breed", "count"])

    df = pd.DataFrame([(record["breed"], record["count"]) for record in breed_data], columns=["breed", "count"])
    return df


def process_gender_distribution(gender_data: list) -> pd.DataFrame:
    """
    Process gender distribution data for visualization.

    Args:
        gender_data (list): Raw gender distribution data from database query

    Returns:
        pd.DataFrame: DataFrame with gender categories and counts suitable for visualization
    """
    if not gender_data:
        return pd.DataFrame(columns=["gender", "count"])

    df = pd.DataFrame([(record["gender"], record["count"]) for record in gender_data], columns=["gender", "count"])

    return df


def process_country_distribution(country_data: list) -> pd.DataFrame:
    """
    Process country distribution data for visualization.

    Args:
        country_data (list): Raw country distribution data from database query

    Returns:
        pd.DataFrame: DataFrame with country names and counts suitable for visualization
    """
    if not country_data:
        return pd.DataFrame(columns=["country", "count"])

    df = pd.DataFrame(
        [(record["country"], record["count"]) for record in country_data], columns=["country", "count"]
    )
    return df


def process_birth_year_distribution(year_data: list) -> pd.DataFrame:
    """
    Process birth year distribution data for visualization.

    Args:
        year_data (list): Raw birth year distribution data from database query

    Returns:
        pd.DataFrame: DataFrame with birth years and counts, filtered for realistic years (1980-2025)
    """
    if not year_data:
        return pd.DataFrame(columns=["birth_year", "count"])

    df = pd.DataFrame(
        [(record["birth_year"], record["count"]) for record in year_data], columns=["birth_year", "count"]
    )

    df["birth_year"] = pd.to_numeric(df["birth_year"], errors="coerce")
    df = df.dropna(subset=["birth_year"])
    df["birth_year"] = df["birth_year"].astype(int)

    return df.sort_values("birth_year")


def process_breed_density_by_country(breed_density_data: list) -> pd.DataFrame:
    """
    Process breed density by country data for visualization.

    Args:
        breed_density_data (list): Raw breed density data from database query

    Returns:
        pd.DataFrame: DataFrame with country names, breed counts, and density metrics
    """
    if not breed_density_data:
        return pd.DataFrame(columns=["country", "breed_count", "total_cats", "density"])

    df = pd.DataFrame(
        [
            (record["country"], record["breed_count"], record["total_cats"], record["density"])
            for record in breed_density_data
        ],
        columns=["country", "breed_count", "total_cats", "density"],
    )

    df["density"] = df["density"].round(2)

    return df


def process_breed_distribution_by_year(breed_year_data: list) -> pd.DataFrame:
    """
    Process breed distribution by year data for visualization.

    Args:
        breed_year_data (list): Raw breed distribution by year data from database query

    Returns:
        pd.DataFrame: DataFrame with years, breed codes, and counts suitable for visualization
    """
    if not breed_year_data:
        return pd.DataFrame(columns=["year", "breed", "count"])

    df = pd.DataFrame(
        [(record["birth_year"], record["breed"], record["count"]) for record in breed_year_data],
        columns=["year", "breed", "count"],
    )

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)

    df = df[(df["year"] >= 1980) & (df["year"] <= 2025)]

    return df.sort_values(["year", "breed"])


def process_breed_timeline_data(breed_timeline_data: list, year_range: list = None) -> pd.DataFrame:
    """
    Process breed timeline data from database into a pandas DataFrame.

    Args:
        breed_timeline_data (list): List of dictionaries containing breed timeline data
        year_range (list, optional): Optional year range filter [min_year, max_year]

    Returns:
        pd.DataFrame: DataFrame with columns for breed, year, and count
    """
    if not breed_timeline_data:
        return pd.DataFrame(columns=["breed", "year", "count"])

    df = pd.DataFrame(breed_timeline_data)

    if year_range and len(year_range) == 2:
        min_year, max_year = year_range
        df = df[(df["year"] >= min_year) & (df["year"] <= max_year)]

    df["year"] = pd.to_numeric(df["year"])
    df["count"] = pd.to_numeric(df["count"])

    return df


def process_family_tree_data(raw_query_results: list) -> tuple[dict, dict]:
    """
    Process the raw Neo4j query results into a flattened data structure and prepare
    visualization-ready data structures.

    Args:
        raw_query_results (list): Raw Neo4j query result records

    Returns:
        tuple: Contains two items:
            - graph_structure_data (dict): Dictionary with 'nodes' and 'edges' arrays for visualization
            - root_cat_details (dict): Details for the root cat (first cat in the results)
    """
    if not raw_query_results:
        return {"nodes": [], "edges": []}, {}

    flattened_cats = []
    for record in raw_query_results:
        cat_node = record.get("cat")
        if not cat_node:
            continue

        cat_data = dict(cat_node.items())

        breed_node = record.get("breed")
        cat_data["breed_code"] = breed_node["breed_code"] if breed_node else None
        cat_data["breed_full_name"] = breed_node["breed_full_name"] if breed_node else None

        color_node = record.get("color")
        cat_data["color_code"] = color_node["color_code"] if color_node else None
        cat_data["color_definition"] = color_node["color_definition"] if color_node else None

        birth_country_node = record.get("birth_country")
        cat_data["birth_country_name"] = birth_country_node["country_name"] if birth_country_node else None
        cat_data["birth_country_alpha_2"] = birth_country_node["alpha_2"] if birth_country_node else None

        current_country_node = record.get("current_country")
        cat_data["current_country_name"] = current_country_node["country_name"] if current_country_node else None
        cat_data["current_country_alpha_2"] = current_country_node["alpha_2"] if current_country_node else None

        cattery_node = record.get("cattery")
        cat_data["cattery_name"] = cattery_node["cattery_name"] if cattery_node else None

        source_db_node = record.get("source_db")
        cat_data["source_db_name"] = source_db_node["source_db_name"] if source_db_node else None

        cat_data["parents"] = [
            p for p in record.get("parents", []) if p is not None and p.get("parent_id") is not None
        ]
        flattened_cats.append(cat_data)

    graph_structure_data = {"nodes": [], "edges": []}
    processed_node_ids = set()
    root_cat_id = None
    root_cat_details = {}

    if flattened_cats:
        root_cat_id = flattened_cats[0].get("id")
        root_cat_details = next((cat for cat in flattened_cats if cat.get("id") == root_cat_id), {})

    for cat_details in flattened_cats:
        current_cat_id = cat_details.get("id")
        if not current_cat_id or current_cat_id in processed_node_ids:
            continue

        graph_structure_data["nodes"].append(cat_details)
        processed_node_ids.add(current_cat_id)

        for parent_info in cat_details.get("parents", []):
            parent_id = parent_info.get("parent_id")
            rel_type = parent_info.get("rel_type")
            if parent_id is not None and rel_type:
                graph_structure_data["edges"].append(
                    {
                        "child_id": current_cat_id,
                        "parent_id": parent_id,
                        "rel_type": rel_type,
                    }
                )

    return graph_structure_data, root_cat_details
