from collections import deque

import networkx as nx
import pandas as pd

from dashboard_app.src.callbacks.callbacks_database import db
from dashboard_app.src.utils.cache import CacheManager
from dashboard_app.src.utils.logger import logger


@CacheManager.memoize()
def calculate_inbreeding_coefficient_modern(cat_id: str) -> float:
    """
    Calculate the inbreeding coefficient for a cat based on common ancestors.

    Args:
        cat_id (str): The ID of the cat to calculate inbreeding coefficient for

    Returns:
        float: Inbreeding coefficient value between 0 and 1
    """

    tree_data = db.get_cat_family_tree_with_path(cat_id, depth=10)

    cat_tree_df = create_cat_tree(tree_data)

    if cat_tree_df.empty:
        return 0.0

    graph = nx.DiGraph()
    for _, row in cat_tree_df.iterrows():
        cat = row["cat_id"]
        mother = row["mother_id"]
        father = row["father_id"]

        if mother != -1:
            graph.add_edge(cat, mother)
        if father != -1:
            graph.add_edge(cat, father)

    cat_row = cat_tree_df[cat_tree_df["cat_id"] == cat_id]
    if cat_row.empty or (cat_row["mother_id"].iloc[0] == -1 and cat_row["father_id"].iloc[0] == -1):
        return 0.0

    mother_id = cat_row["mother_id"].iloc[0]
    father_id = cat_row["father_id"].iloc[0]

    if mother_id == -1 or father_id == -1:
        return 0.0

    try:
        mother_ancestors = set(nx.descendants(graph, mother_id))
        father_ancestors = set(nx.descendants(graph, father_id))
    except nx.NetworkXError:
        return 0.0

    common_ancestors = mother_ancestors.intersection(father_ancestors)

    if not common_ancestors:
        return 0.0

    inbreeding_coeff = 0.0
    processed_paths = set()  # Track processed path combinations to avoid double-counting

    for ancestor in common_ancestors:
        try:
            # Find all simple paths from mother to this ancestor
            paths_mother_to_ancestor = list(nx.all_simple_paths(graph, source=mother_id, target=ancestor))
            # Find all simple paths from father to this ancestor
            paths_father_to_ancestor = list(nx.all_simple_paths(graph, source=father_id, target=ancestor))

            for p_m in paths_mother_to_ancestor:
                for p_f in paths_father_to_ancestor:
                    # Create a unique identifier for this path combination
                    path_key = (tuple(p_m), tuple(p_f))

                    # Skip if we've already processed this path combination
                    if path_key in processed_paths:
                        continue

                    # Add to processed paths
                    processed_paths.add(path_key)

                    # Check if this path combination is valid:
                    # 1. The ancestor should appear exactly once in each path
                    # 2. No other common ancestor should appear in either path (except at the end)

                    # First, check if ancestor appears exactly once in each path
                    if p_m.count(ancestor) != 1 or p_f.count(ancestor) != 1:
                        continue

                    # Check if any other common ancestor appears in the mother's path (excluding the end)
                    if any(node in common_ancestors for node in p_m[:-1] if node != ancestor):
                        continue

                    # Check if any other common ancestor appears in the father's path (excluding the end)
                    if any(node in common_ancestors for node in p_f[:-1] if node != ancestor):
                        continue

                    # Calculate path lengths (number of generations)
                    n1 = len(p_m) - 1  # Number of edges in path from mother
                    n2 = len(p_f) - 1  # Number of edges in path from father

                    # Apply Wright's formula: F = (1/2)^(n1+n2+1)
                    # Assuming Fa = 0 (ancestor's own inbreeding coefficient is zero)
                    path_contribution = 0.5 ** (n1 + n2 + 1)

                    print(
                        f"Valid path through ancestor {ancestor}: "
                        f"Mother path length={n1}, Father path length={n2}, "
                        f"Contribution={path_contribution}"
                    )

                    inbreeding_coeff += path_contribution

        except nx.NodeNotFound:
            # This might happen if, for some reason, an ID is not in the graph,
            # though mother_id, father_id, and ancestor should be.
            logger.warning(
                f"NodeNotFound exception for ancestor {ancestor}, mother {mother_id}, or father {father_id} during path finding."
            )
            continue
        except Exception as e:
            logger.error(f"An unexpected error occurred for ancestor {ancestor}: {e}")
            continue

    return min(inbreeding_coeff, 1.0)


def create_cat_tree(tree_data: list) -> pd.DataFrame:
    """
    Create a DataFrame representing the family tree of a cat with parent relationships.

    Args:
        tree_data (list): List of dictionaries containing cat family tree data

    Returns:
        pd.DataFrame: DataFrame with cat_id, mother_id, and father_id columns
    """
    if not tree_data:
        return pd.DataFrame(columns=["cat_id", "mother_id", "father_id"])

    cat_relationships = {}

    for record in tree_data:
        path = record["path"]
        nodes = path.nodes
        relationships = path.relationships

        for rel in relationships:
            child_node = rel.start_node
            parent_node = rel.end_node
            relationship_type = rel.type

            child_props = dict(child_node.items())
            parent_props = dict(parent_node.items())

            child_id = child_props.get("id")
            parent_id = parent_props.get("id")

            if not child_id or not parent_id:
                continue

            if child_id not in cat_relationships:
                cat_relationships[child_id] = {"cat_id": child_id, "mother_id": -1, "father_id": -1}

            if relationship_type == "HAS_FATHER":
                cat_relationships[child_id]["father_id"] = parent_id
            elif relationship_type == "HAS_MOTHER":
                cat_relationships[child_id]["mother_id"] = parent_id

    for record in tree_data:
        nodes = record["path"].nodes
        for node in nodes:
            node_props = dict(node.items())
            cat_id = node_props.get("id")

            if cat_id and cat_id not in cat_relationships:
                cat_relationships[cat_id] = {"cat_id": cat_id, "mother_id": -1, "father_id": -1}

    df = pd.DataFrame.from_dict(list(cat_relationships.values()))

    return df


def calculate_inbreeding_coefficient_old(cat_id: str) -> float:
    tree_data = db.get_cat_family_tree(cat_id, depth=10)
    cat_tree_df = create_cat_tree(tree_data)

    inbreeding_coefficient = 0
    relationship_coefficient = 0
    duplicate_cat_inbreeding_coefficient = 0

    common_ancestor = find_first_common_ancestor(cat_tree_df)

    if common_ancestor.empty:
        return 0.0

    ancestor_cat_tree = db.get_cat_family_tree(common_ancestor.cat_id, depth=10)
    ancestor_cat_tree_df = create_cat_tree(ancestor_cat_tree)

    common_ancestor_of_ancestor = find_first_common_ancestor(ancestor_cat_tree_df)

    if not common_ancestor_of_ancestor.empty:
        mother_id = ancestor_cat_tree_df.iloc[0].mother_id
        father_id = ancestor_cat_tree_df.iloc[0].father_id
        mother = ancestor_cat_tree_df[ancestor_cat_tree_df["cat_id"] == mother_id].iloc[0]
        father = ancestor_cat_tree_df[ancestor_cat_tree_df["cat_id"] == father_id].iloc[0]

        distance_mother = find_distance(ancestor_cat_tree_df, mother, common_ancestor_of_ancestor)
        distance_father = find_distance(ancestor_cat_tree_df, father, common_ancestor_of_ancestor)

        duplicate_cat_inbreeding_coefficient = coefficient_inbreeding(distance_mother, distance_father, 0)

    mother_id = cat_tree_df.iloc[0].mother_id
    father_id = cat_tree_df.iloc[0].father_id
    mother = cat_tree_df[cat_tree_df["cat_id"] == mother_id].iloc[0]
    father = cat_tree_df[cat_tree_df["cat_id"] == father_id].iloc[0]

    distance_mother = find_distance(cat_tree_df, mother, common_ancestor)
    distance_father = find_distance(cat_tree_df, father, common_ancestor)

    inbreeding_coefficient = coefficient_inbreeding(
        distance_mother, distance_father, duplicate_cat_inbreeding_coefficient
    )

    relationship_coefficient = coefficient_relationship(distance_mother, distance_father)

    return 0.0


def find_first_common_ancestor(cat_tree_df):
    if cat_tree_df.empty:
        return pd.Series()

    visited_nodes = set()
    queue = deque()

    queue.append(cat_tree_df.iloc[0])

    try:
        while queue:
            current_node = queue.popleft()
            cat_id = current_node.cat_id

            if cat_id in visited_nodes:
                return current_node
            visited_nodes.add(cat_id)

            if current_node.mother_id != -1:
                mother = cat_tree_df[cat_tree_df["cat_id"] == current_node.mother_id].iloc[0]
                queue.append(mother)
            if current_node.father_id != -1:
                father = cat_tree_df[cat_tree_df["cat_id"] == current_node.father_id].iloc[0]
                queue.append(father)

    except Exception as e:
        logger.error(f"An error occurred during the search: {e}")
        return pd.Series()

    return pd.Series()


def find_distance(cat_tree_df, cat_1, cat_2):
    if cat_tree_df.empty:
        return -1

    visited_nodes = set()
    queue = deque()

    queue.append((cat_1, 0))

    try:
        while queue:
            current_node, distance = queue.popleft()
            cat_id = current_node.cat_id

            if cat_id == cat_2.cat_id:
                return distance

            if current_node.mother_id != -1 and current_node.mother_id not in visited_nodes:
                mother = cat_tree_df[cat_tree_df["cat_id"] == current_node.mother_id].iloc[0]
                queue.append((mother, distance + 1))
                visited_nodes.add(current_node.mother_id)
            if current_node.father_id != -1:
                father = cat_tree_df[cat_tree_df["cat_id"] == current_node.father_id].iloc[0]
                queue.append((father, distance + 1))
                visited_nodes.add(current_node.father_id)

    except Exception as e:
        logger.error(f"An error occurred during the search: {e}")
        return -1

    return -1


def coefficient_inbreeding(n1: int, n2: int, F_a: float = 0) -> float:
    try:
        exponent = n1 + n2 + 1
        Fx = ((1 / 2) ** exponent) * (1 + F_a)
        return Fx
    except TypeError:
        raise TypeError("Both numbers of generations from a common ancestors must be integers.")


def coefficient_relationship(n1: int, n2: int) -> float:
    try:
        f = 0.5 ** (n1 + n2)
        return f
    except TypeError:
        raise TypeError("Both numbers of generations from a common ancestors must be integers.")
