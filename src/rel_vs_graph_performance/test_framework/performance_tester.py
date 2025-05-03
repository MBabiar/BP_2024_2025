import math
import time
from statistics import mean, median

from .db_connector import DatabaseConnector
from .query_loader import QueryLoader


class PerformanceTester:
    """
    Class to conduct performance tests between Neo4j and PostgreSQL.

    This class handles running queries with different parameters and
    collecting timing statistics.
    """

    def __init__(self):
        """Initialize performance tester with database connections."""
        self.db_connector = DatabaseConnector()

    def time_postgres_query(self, query, params, iterations):
        """
        Time PostgreSQL query execution.

        Args:
            query (str): SQL query to execute
            params (dict): Parameters to use in the query
            iterations (int): Number of times to run the query

        Returns:
            list: Execution times in seconds for each iteration
        """
        conn = self.db_connector.get_postgres_connection()
        cursor = conn.cursor()

        times = []
        for _ in range(iterations):
            start_time = time.time()
            cursor.execute(query, params)
            cursor.fetchall()
            end_time = time.time()
            times.append(end_time - start_time)

        cursor.close()
        return times

    def time_neo4j_query(self, query, params, iterations):
        """
        Time Neo4j query execution.

        Args:
            query (str): Cypher query to execute
            params (dict): Parameters to use in the query
            iterations (int): Number of times to run the query

        Returns:
            list: Execution times in seconds for each iteration
        """
        driver = self.db_connector.get_neo4j_driver()

        times = []
        with driver.session() as session:
            for _ in range(iterations):
                start_time = time.time()
                session.run(query, params).consume()
                end_time = time.time()
                times.append(end_time - start_time)

        return times

    def calculate_statistics_without_outliers(self, times):
        """
        Calculate statistics after removing 10% of the min and max values (outliers).

        Only apply outlier removal for datasets with sufficient size (>= 10 elements).
        For smaller datasets, use a more conservative approach.

        Args:
            times (list): List of execution times

        Returns:
            dict: Dictionary with min, max, avg, and median statistics
        """
        if len(times) <= 2:
            return {
                "min": min(times),
                "max": max(times),
                "avg": mean(times),
                "median": median(times),
                "times": times,
            }

        sorted_times = sorted(times)

        if len(times) >= 10:
            remove_count = math.ceil(len(times) * 0.1)
            filtered_times = sorted_times[remove_count:-remove_count] if remove_count > 0 else sorted_times
        elif len(times) >= 5:
            filtered_times = sorted_times[1:-1]
        else:
            filtered_times = sorted_times

        return {
            "min": min(filtered_times),
            "max": max(filtered_times),
            "avg": mean(filtered_times),
            "median": median(filtered_times),
            "times": times,
        }

    def run_test(self, query_type, cat_id, depth, iterations):
        """
        Run performance comparison between Neo4j and PostgreSQL.

        Args:
            query_type (str): Type of query to run (tree_ancestry, tree_all, or breed_distribution)
            cat_id (int): ID of the cat to query
            depth (int): Maximum depth/generations to retrieve (not used for breed_distribution)
            iterations (int): Number of times to run each query

        Returns:
            dict: Test results with statistics for both databases
        """
        sql_path, cypher_path = QueryLoader.get_query_paths(query_type)

        sql_query = QueryLoader.load_sql_query(sql_path)
        cypher_query = QueryLoader.load_cypher_query(cypher_path)

        if query_type in ["tree_ancestry", "tree_all"]:
            cypher_query = cypher_query.replace("{depth}", str(depth))
            sql_params = {"cat_id": cat_id, "depth": depth}
        else:
            sql_params = {}

        cypher_params = {"cat_id": cat_id} if query_type != "breed_distribution" else {}

        try:
            pg_times = self.time_postgres_query(sql_query, sql_params, iterations)
            neo4j_times = self.time_neo4j_query(cypher_query, cypher_params, iterations)

            pg_stats = self.calculate_statistics_without_outliers(pg_times)
            neo_stats = self.calculate_statistics_without_outliers(neo4j_times)

            pg_avg = pg_stats["avg"]
            neo_avg = neo_stats["avg"]

            if pg_avg < neo_avg:
                winner = "PostgreSQL"
                factor = neo_avg / pg_avg
            else:
                winner = "Neo4j"
                factor = pg_avg / neo_avg

            return {
                "postgres": pg_stats,
                "neo4j": neo_stats,
                "winner": winner,
                "factor": factor,
                "params": {"cat_id": cat_id, "depth": depth, "iterations": iterations, "query_type": query_type},
            }

        except Exception as e:
            print(f"Error during test: {e}")
            return {
                "error": str(e),
                "params": {"cat_id": cat_id, "depth": depth, "iterations": iterations, "query_type": query_type},
            }

    def cleanup(self):
        """Close all database connections."""
        self.db_connector.close()
