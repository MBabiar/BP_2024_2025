import re
from pathlib import Path


class QueryLoader:
    """
    Utility class to load SQL and Cypher queries from files.

    Handles loading, cleaning and parameter substitution for both
    PostgreSQL and Neo4j queries.
    """

    @staticmethod
    def load_sql_query(file_path):
        """
        Load a SQL query from a file.

        Args:
            file_path (str): Path to the SQL file

        Returns:
            str: The SQL query as a string
        """
        with open(file_path, "r") as f:
            return f.read().strip()

    @staticmethod
    def load_cypher_query(file_path):
        """
        Load a Cypher query from a file, removing comments that would cause syntax errors.

        Args:
            file_path (str): Path to the Cypher query file

        Returns:
            str: The cleaned Cypher query
        """
        with open(file_path, "r") as f:
            content = f.read()

        content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)

        content = content.strip()

        return content

    @staticmethod
    def get_query_paths(query_type="tree_ancestry"):
        """
        Get paths to SQL and Cypher query files based on query type.

        Args:
            query_type (str): "tree_ancestry" for ancestry-only queries,
                             "tree_all" for full cat information queries,
                             "breed_distribution" for breed distribution stats

        Returns:
            tuple: (sql_path, cypher_path) containing paths to corresponding query files
        """
        project_root = Path(__file__).parent.parent.parent.parent

        if query_type == "tree_ancestry":
            sql_path = project_root / "src" / "rel_vs_graph_performance" / "queries" / "rel_tree_ancestry.sql"
            cypher_path = (
                project_root / "src" / "rel_vs_graph_performance" / "queries" / "neo_tree_ancestry.cypher"
            )
        elif query_type == "breed_distribution":
            sql_path = project_root / "src" / "rel_vs_graph_performance" / "queries" / "rel_breed_distribution.sql"
            cypher_path = (
                project_root / "src" / "rel_vs_graph_performance" / "queries" / "neo_breed_distribution.cypher"
            )
        elif query_type == "tree_all":
            sql_path = project_root / "src" / "rel_vs_graph_performance" / "queries" / "rel_tree_all.sql"
            cypher_path = project_root / "src" / "rel_vs_graph_performance" / "queries" / "neo_tree_all.cypher"
        else:
            sql_path = project_root / "src" / "rel_vs_graph_performance" / "queries" / "rel_tree_ancestry.sql"
            cypher_path = (
                project_root / "src" / "rel_vs_graph_performance" / "queries" / "neo_tree_ancestry.cypher"
            )

        return sql_path, cypher_path
