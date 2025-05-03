import os
from pathlib import Path

import pandas as pd
from neo4j import GraphDatabase
from termcolor import colored
from tqdm import tqdm

from src.utils import custom_print, load_data_config


def query_neo4j(driver: GraphDatabase.driver, query: str) -> list:
    """
    Load data from Neo4j database using the provided query.
    """
    with driver.session() as session:
        result = session.run(query)
        return [dict(record.items()) for record in result]


def load_csv_data(file_name: str) -> pd.DataFrame:
    """
    Load data from a CSV file.

    :param file_name: Name of the CSV file to load
    """
    data_paths, column_types = load_data_config()
    data_path_final = Path(data_paths["final"])
    csv_path = data_path_final / file_name
    return pd.read_csv(csv_path, dtype=column_types, low_memory=False)


class BaseDataIntegrityTester:
    """
    Base class for testing data integrity between Neo4j database and CSV files.
    Provides common functionality for all node types.
    """

    def __init__(self, driver: GraphDatabase.driver):
        """
        Initialize the tester with a Neo4j driver.

        :param driver: Neo4j driver object
        """
        self.driver = driver
        self.data_dir = os.path.join("data", "final_data")

    def load_neo4j_data(self, node_label: str, properties: list, batch_size: int = 100000) -> list:
        """
        Loads data from Neo4j in batches.

        :param node_label: The label of the nodes to retrieve
        :param properties: List of properties to retrieve
        :param batch_size: Size of each batch for retrieving data
        :return: List containing the Neo4j data
        """
        properties_str = ", ".join([f"n.{prop}" for prop in properties])

        skip = 0
        all_neo4j_data = []

        count_query = f"MATCH (n:{node_label}) RETURN COUNT(n) AS total"
        total_records = query_neo4j(self.driver, count_query)[0]["total"]

        with tqdm(total=total_records, desc=f"Processing {node_label} nodes", unit="records") as pbar:
            while True:
                query = f"""
                MATCH (n:{node_label})
                RETURN {properties_str}
                SKIP {skip} LIMIT {batch_size}
                """
                batch_data = query_neo4j(self.driver, query)

                if not batch_data:
                    break

                all_neo4j_data.extend(batch_data)
                skip += batch_size

                pbar.update(len(batch_data))

        return all_neo4j_data

    def transform_neo4j_data(self, neo4j_data: list) -> pd.DataFrame:
        """
        Transforms Neo4j data into a DataFrame format suitable for comparison.

        :param neo4j_data: Raw data from Neo4j
        :return: Transformed DataFrame
        """
        neo4j_df = pd.DataFrame(neo4j_data)

        if neo4j_df.empty:
            return neo4j_df

        neo4j_df.columns = [col.split(".")[-1] for col in neo4j_df.columns]

        if "id" in neo4j_df.columns:
            neo4j_df = neo4j_df.set_index("id")

        if "id" in neo4j_df.columns:
            neo4j_df = neo4j_df.sort_index()

        return neo4j_df

    def compare_with_csv(self, neo4j_df: pd.DataFrame, csv_name: str, required_columns: list) -> bool:
        """
        Compares Neo4j data with CSV data.

        :param neo4j_df: DataFrame containing Neo4j data
        :param csv_name: Name of the CSV file to compare with
        :param required_columns: List of columns to compare
        :return: True if data matches, False otherwise
        """
        csv_data = load_csv_data(csv_name)

        if "id" in required_columns:
            csv_columns = required_columns
            csv_data = csv_data[csv_columns]
            csv_data = csv_data.set_index("id")
            if neo4j_df.equals(csv_data):
                print(colored("Data integrity test passed.", "green"))
                return True
            else:
                print(colored("Data integrity test failed.", "red"))
                diff = neo4j_df.compare(csv_data)
                custom_print(colored(diff, "yellow"), level=2)
                return False

    def test_integrity(self, node_label: str, properties: list, csv_name: str) -> bool:
        """
        Generic method to test data integrity for any node type.

        :param node_label: Neo4j node label
        :param properties: List of properties to check
        :param csv_name: Name of the CSV file to compare with
        :return: True if test passes, False otherwise
        """
        custom_print(f"Testing {node_label} nodes data integrity")

        neo4j_data = self.load_neo4j_data(node_label, properties)
        neo4j_df = self.transform_neo4j_data(neo4j_data)
        return self.compare_with_csv(neo4j_df, csv_name, properties)
