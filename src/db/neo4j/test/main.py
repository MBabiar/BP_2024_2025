import sys
import time

from neo4j import GraphDatabase, basic_auth
from node_testers import (
    BreedsTester,
    CatsTester,
    CatteriesTester,
    ColorsTester,
    CountriesTester,
    SourceDatabaseTester,
)
from relationship_tester import RelationshipTester
from termcolor import colored

from src.utils import custom_print, load_config


def connect_to_neo4j():
    """
    Connect to Neo4j database using credentials from config.json.
    """
    retries = 3

    config = load_config()
    try:
        neo4j_config = config.get("graph_database", {})
        uri = neo4j_config.get("uri", "bolt://localhost:7687")
        username = neo4j_config.get("username", "neo4j")
        password = neo4j_config.get("password", "root0123")
    except Exception as e:
        print(f"Error loading Neo4j configuration: {e}")
        sys.exit(1)

    for attempt in range(retries):
        try:
            driver = GraphDatabase.driver(uri, auth=basic_auth(username, password))

            with driver.session() as session:
                session.run("MATCH (n) RETURN COUNT(n) LIMIT 1")

            return driver
        except Exception as e:
            if attempt < retries - 1:
                print(f"Connection attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(5)
            else:
                print(f"Error connecting to Neo4j after {retries} attempts: {e}")
                sys.exit(1)


def check_empty_neo4j(driver: GraphDatabase.driver) -> bool:
    """
    Check if the Neo4j database is empty.

    :param driver: Neo4j driver instance
    :return: True if the database is empty, False otherwise
    """
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN COUNT(n) AS count")
        count = result.single()["count"]
        return count == 0


def show_end_results(results: dict) -> None:
    """
    Display the end results of the data integrity tests.

    :param results: Dictionary containing test results
    """
    custom_print("\nData Integrity Test Results:")

    all_passed = all(result for result in results.values())
    if all_passed:
        custom_print("All tests passed!", level=2)
    else:
        custom_print("Some tests failed. Please check the details below.", level=2)
        for label, result in results.items():
            if not result:
                print(f"{label}: {colored('Failed', 'red')}")


def main():
    custom_print("Connecting to Neo4j database")
    driver = connect_to_neo4j()
    custom_print("Connected to Neo4j database", level=2)

    if check_empty_neo4j(driver):
        custom_print("Neo4j database is empty. Exiting.", level=2)
        driver.close()
        sys.exit(0)

    try:
        cats_tester = CatsTester(driver)
        cats_result = cats_tester.test_integrity()

        breeds_tester = BreedsTester(driver)
        breeds_result = breeds_tester.test_integrity()

        colors_tester = ColorsTester(driver)
        colors_result = colors_tester.test_integrity()

        countries_tester = CountriesTester(driver)
        countries_result = countries_tester.test_integrity()

        catteries_tester = CatteriesTester(driver)
        catteries_result = catteries_tester.test_integrity()

        source_db_tester = SourceDatabaseTester(driver)
        source_db_result = source_db_tester.test_integrity()

        relationship_tester = RelationshipTester(driver)
        relationship_results = relationship_tester.test_all_relationships()

        results = {
            "Cats": cats_result,
            "Breeds": breeds_result,
            "Colors": colors_result,
            "Countries": countries_result,
            "Catteries": catteries_result,
            "Source Databases": source_db_result,
            **relationship_results,
        }
        show_end_results(results)

    finally:
        driver.close()


if __name__ == "__main__":
    main()
