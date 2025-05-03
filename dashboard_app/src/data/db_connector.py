import json
import os
import socket
from pathlib import Path

from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable

from dashboard_app.src.utils.logger import logger


class Neo4jConnector:
    def __init__(self):
        """
        Initialize Neo4j database connection using configuration from config.json
        """
        config_path = Path("config/config.json")
        with open(config_path, "r") as f:
            config = json.load(f)

        is_docker = self._is_running_in_docker()
        config_key = "graph_database_docker" if is_docker else "graph_database"

        neo4j_config = config.get(config_key, {})
        self.host = neo4j_config.get("host")
        self.port = neo4j_config.get("port")
        self.username = neo4j_config.get("user")
        self.password = neo4j_config.get("password")

        self.uri = f"bolt://{self.host}:{self.port}"

        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            self._closed = False
            self.connection_error = None
        except Exception as e:
            self.connection_error = f"Failed to initialize Neo4j driver: {str(e)}"
            self._closed = True
            logger.error(f"Error initializing Neo4j driver: {e}")

    def _is_running_in_docker(self):
        """
        Detect if the application is running inside a Docker container

        Returns:
            bool: True if running in Docker, False otherwise
        """
        if os.environ.get("RUNNING_IN_DOCKER") == "true":
            return True

        return False

    def check_connection(self):
        """
        Check if the Neo4j database connection is working

        Returns:
            bool: True if connection is successful, False otherwise
        """
        self.connection_error = None

        if not self._is_host_reachable():
            self.connection_error = f"Cannot reach Neo4j host at {self.host}:{self.port}. The database might be down or network connectivity issues exist."
            return False

        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS test")
                result.single()
                logger.info(f"Successfully connected to Neo4j at {self.uri}")
                return True
        except AuthError as e:
            self.connection_error = f"Authentication failed for user '{self.username}'. Please check username and password. Error: {str(e)}"
            logger.error(f"Authentication error: {e}")
            return False
        except ServiceUnavailable as e:
            self.connection_error = f"Service unavailable: {str(e)}"
            logger.warning(f"Service unavailable: {e}")
            return False
        except Exception as e:
            self.connection_error = f"Unexpected error connecting to database: {str(e)}"
            logger.error(f"Unexpected error: {e}")
            return False

    def _is_host_reachable(self):
        """
        Check if the Neo4j host is reachable at network level

        Returns:
            bool: True if host is reachable, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.host, self.port))
            sock.close()

            if result == 0:
                return True
            else:
                logger.warning(f"Cannot connect to {self.host}:{self.port}. Connection refused.")
                return False

        except socket.error as e:
            logger.error(f"Socket error while checking host reachability: {e}")
            return False

    def close(self):
        """Close the Neo4j driver connection"""
        if not self._closed:
            try:
                self.driver.close()
                self._closed = True
            except Exception as e:
                logger.error(f"Error closing Neo4j driver: {e}")

    def __del__(self):
        """Ensure driver is closed on object destruction"""
        try:
            self.close()
        except Exception as e:
            logger.error(f"Error during driver cleanup: {e}")

    def query(self, cypher_query, parameters=None):
        """
        Execute a Neo4j Cypher query and return the results

        Args:
            cypher_query (str): The Cypher query to execute
            parameters (dict, optional): Parameters for the query

        Returns:
            list: List of records from the query result
        """
        if parameters is None:
            parameters = {}

        try:
            with self.driver.session() as session:
                result = session.run(cypher_query, parameters)
                return [record for record in result]
        except Exception as e:
            self.connection_error = f"Query error: {str(e)}"
            logger.error(f"Error executing query: {e}")
            return []

    # ----------------------------------------------------------------------------------------------------
    # Common queries for the dashboard
    # ----------------------------------------------------------------------------------------------------
    def get_cat_count(self) -> int:
        """
        Get the total number of cats in the database.

        Returns:
            int: Total count of cats in the database
        """
        query = "MATCH (c:Cat) RETURN COUNT(c) AS cat_count"
        result = self.query(query)
        return result[0]["cat_count"] if result else 0

    def get_breed_count(self) -> int:
        """
        Get the total number of distinct breeds.

        Returns:
            int: Total count of distinct breeds in the database
        """
        query = "MATCH (b:Breed) RETURN COUNT(DISTINCT b.breed_code) AS breed_count"
        result = self.query(query)
        return result[0]["breed_count"] if result else 0

    def get_country_count(self) -> int:
        """
        Get the total number of distinct countries.

        Returns:
            int: Total count of distinct countries in the database
        """
        query = "MATCH (co:Country) RETURN COUNT(DISTINCT co.country_name) AS country_count"
        result = self.query(query)
        return result[0]["country_count"] if result else 0

    def get_source_db_count(self) -> int:
        """
        Get the total number of source databases.

        Returns:
            int: Total count of source databases in the database
        """
        query = "MATCH (s:SourceDB) RETURN COUNT(s) AS db_count"
        result = self.query(query)
        return result[0]["db_count"] if result else 0

    def get_breed_distribution(self) -> list:
        """
        Get distribution of cats by breed.

        Returns:
            list: List of records containing breed code and cat count for each breed
        """
        query = """
        MATCH (c:Cat)-[:BELONGS_TO_BREED]->(b:Breed)
        WHERE b.breed_code <> 'unknown'
        RETURN b.breed_code AS breed, COUNT(c) AS count
        ORDER BY count DESC
        """
        return self.query(query)

    def get_gender_distribution(self) -> list:
        """
        Get distribution of cats by gender.

        Returns:
            list: List of records containing gender and cat count for each gender
        """
        query = """
        MATCH (c:Cat)
        RETURN c.gender AS gender, COUNT(c) AS count
        ORDER BY count DESC
        """
        return self.query(query)

    def get_country_distribution(self) -> list:
        """
        Get distribution of cats by country of origin.

        Returns:
            list: List of records containing country name and cat count for each country
        """
        query = """
        MATCH (c:Cat)-[:BORN_IN]->(co:Country)
        RETURN co.country_name AS country, COUNT(c) AS count
        ORDER BY count DESC
        """
        return self.query(query)

    def get_birth_year_distribution(self) -> list:
        """
        Get distribution of cats by birth year.

        Returns:
            list: List of records containing birth year and cat count for each year
        """
        query = """
        MATCH (c:Cat)
        WHERE c.date_of_birth <> '1111-11-11 00:00:00'
        WITH SUBSTRING(c.date_of_birth, 0, 4) AS birth_year, COUNT(c) AS count
        WHERE birth_year <> ''
        RETURN birth_year, count
        ORDER BY birth_year
        """
        return self.query(query)

    def get_birth_year_range(self) -> tuple:
        """
        Get only the minimum and maximum birth years from the database.
        This is more efficient than fetching the full distribution.

        Returns:
            tuple: (min_year, max_year) containing the minimum and maximum birth years as integers
        """
        query = """
        MATCH (c:Cat)
        WHERE c.date_of_birth <> '1111-11-11 00:00:00'
        WITH SUBSTRING(c.date_of_birth, 0, 4) AS birth_year
        WHERE birth_year <> '' AND birth_year =~ '^[0-9]+$'
        RETURN 
            MIN(toInteger(birth_year)) AS min_year,
            MAX(toInteger(birth_year)) AS max_year
        """
        return self.query(query)

    def get_cat_family_tree_with_path(self, cat_id: str, depth: int) -> list:
        """
        Get family tree for a specific cat.

        Args:
            cat_id (str): ID of the cat to get family tree for
            depth (int): Maximum number of generations to include in the family tree

        Returns:
            list: List of records containing path data for the cat's family tree
        """
        query = f"""
        MATCH path = (c:Cat {{id: $cat_id}})-[:HAS_FATHER|HAS_MOTHER*1..{depth}]->(ancestor:Cat)
        RETURN path
        """
        return self.query(query, {"cat_id": cat_id})

    def get_cat_family_tree(self, cat_id: str, depth: int = 3) -> list:
        """
        Get raw family tree data for a specific cat, including detailed information for all nodes.

        Args:
            cat_id (str): ID of the cat to get family tree for
            depth (int): Maximum number of generations to include in the family tree

        Returns:
            list: Raw Neo4j query results containing detailed cat and relationship data.
                  Returns empty list on error or if no data.
        """
        query = f"""
        MATCH path = (root:Cat {{id: $cat_id}})-[:HAS_FATHER|HAS_MOTHER*0..{depth}]->(ancestor:Cat)
        WITH root, COLLECT(DISTINCT ancestor) AS ancestors
        WITH root + ancestors AS family_nodes

        UNWIND family_nodes AS cat

        OPTIONAL MATCH (cat)-[:BELONGS_TO_BREED]->(breed:Breed)
        OPTIONAL MATCH (cat)-[:HAS_COLOR]->(color:Color)
        OPTIONAL MATCH (cat)-[:BORN_IN]->(birth_country:Country)
        OPTIONAL MATCH (cat)-[:LIVES_IN]->(current_country:Country)
        OPTIONAL MATCH (cat)-[:BRED_BY]->(cattery:Cattery)
        OPTIONAL MATCH (cat)-[:FROM_DATABASE]->(source_db:SourceDB)

        OPTIONAL MATCH (cat)-[r:HAS_FATHER|HAS_MOTHER]->(parent:Cat)
        WHERE parent IN family_nodes

        RETURN cat,
               breed,
               color,
               birth_country,
               current_country,
               cattery,
               source_db,
               COLLECT(DISTINCT CASE WHEN parent IS NOT NULL THEN {{rel_type: TYPE(r), parent_id: parent.id}} ELSE null END) AS parents
        """
        try:
            return self.query(query, {"cat_id": cat_id, "depth": depth})
        except Exception as e:
            logger.error(f"Error fetching family tree data for cat {cat_id}: {e}")
            self.connection_error = f"Family tree query error: {str(e)}"
            return []

    def search_cats_by_name_or_id(self, search_term: str, limit: int = 100) -> list:
        """
        Search for cats by name or ID using a hybrid approach.

        Args:
            search_term (str): Term to search for in cat names or IDs
            limit (int): Maximum number of results to return

        Returns:
            list: List of dictionaries containing matched cat data (id, name, gender, date_of_birth)
        """
        results = []

        if search_term.isdigit():
            search_term_int = int(search_term)
            id_query = """
            MATCH (c:Cat {id: $search_id})
            RETURN c.id AS id, c.name AS name, c.gender as gender, c.date_of_birth as date_of_birth
            """
            id_results = self.query(id_query, {"search_id": search_term_int})
            results.extend(id_results)

        if len(results) < limit:
            name_query = """
            CALL db.index.fulltext.queryNodes('cat_name_fulltext', $search_term) YIELD node, score
            RETURN node.id AS id, node.name AS name, node.gender as gender, node.date_of_birth as date_of_birth
            ORDER BY score DESC
            LIMIT $remaining_limit
            """
            name_results = self.query(
                name_query, {"search_term": search_term, "remaining_limit": limit - len(results)}
            )
            results.extend(name_results)

        results = [
            {
                "id": record["id"],
                "name": record["name"],
                "gender": record["gender"],
                "date_of_birth": record["date_of_birth"],
            }
            for record in results
        ]

        return results

    def get_breed_density_by_country(self, breed_code: str) -> list:
        """
        Get density of a specific breed by country.

        Args:
            breed_code (str): Breed code to filter for.

        Returns:
            list: List of records containing country name, breed count, and density metrics
        """
        query = """
        MATCH (cat:Cat)-[:BELONGS_TO_BREED]->(breed:Breed {breed_code: $breed_code})
        MATCH (cat)-[:BORN_IN]->(country:Country)
        WITH country.country_name AS country, COUNT(cat) AS breed_count
        
        MATCH (c:Cat)-[:BORN_IN]->(co:Country {country_name: country})
        WITH country, breed_count, COUNT(c) AS total_cats
        
        WITH country, breed_count, total_cats, 
             toFloat(breed_count) / toFloat(total_cats) * 100.0 AS density
        
        RETURN country, breed_count, total_cats, density
        ORDER BY density DESC
        """
        return self.query(query, {"breed_code": breed_code})

    def get_breed_timeline_data(self, selected_breeds=None, year_range=None):
        """
        Get breed count data by year for visualization.

        Args:
            selected_breeds (list): Optional list of breed codes to filter for
            year_range (list): Optional year range [min_year, max_year] to filter for

        Returns:
            list: List of dictionaries with breed, year and count data
        """
        try:
            with self.driver.session() as session:
                query = """
                MATCH (c:Cat)-[:BELONGS_TO_BREED]->(b:Breed)
                WHERE c.date_of_birth IS NOT NULL AND c.date_of_birth <> '1111-11-11 00:00:00'
                WITH b.breed_code AS breed, SUBSTRING(c.date_of_birth, 0, 4) AS birth_year, count(c) AS count
                WHERE birth_year <> ''
                """

                params = {}
                if selected_breeds and len(selected_breeds) > 0:
                    query += " AND breed IN $breeds"
                    params["breeds"] = selected_breeds

                if year_range and len(year_range) == 2:
                    query += " AND toInteger(birth_year) >= $min_year AND toInteger(birth_year) <= $max_year"
                    params["min_year"] = year_range[0]
                    params["max_year"] = year_range[1]

                query += """
                RETURN breed, toInteger(birth_year) AS year, count
                ORDER BY year, breed
                """

                result = session.run(query, params)
                return [record.data() for record in result]

        except Exception as e:
            logger.error(f"Error fetching breed timeline data: {e}")
            return []

    def get_detailed_cat_information(self, cat_id: str) -> dict:
        """
        Get detailed cat information including related entities.

        Args:
            cat_id (str): ID of the cat to get information for

        Returns:
            dict: Dictionary containing all cat information including relationships
        """
        query = """
        MATCH (cat:Cat {id: $cat_id})
        
        OPTIONAL MATCH (cat)-[:BELONGS_TO_BREED]->(breed:Breed)
        OPTIONAL MATCH (cat)-[:HAS_COLOR]->(color:Color)
        OPTIONAL MATCH (cat)-[:BORN_IN]->(birth_country:Country)
        OPTIONAL MATCH (cat)-[:LIVES_IN]->(current_country:Country)
        OPTIONAL MATCH (cat)-[:BRED_BY]->(cattery:Cattery)
        OPTIONAL MATCH (cat)-[:FROM_DATABASE]->(source_db:SourceDB)
        
        RETURN cat,
               breed,
               color,
               birth_country,
               current_country,
               cattery,
               source_db
        """
        result = self.query(query, {"cat_id": cat_id})

        if not result:
            return {}

        record = result[0]
        cat_props = dict(record["cat"].items()) if record.get("cat") else {}

        cat_props["breed"] = dict(record["breed"].items()) if record.get("breed") else {}
        cat_props["color"] = dict(record["color"].items()) if record.get("color") else {}
        cat_props["birth_country"] = dict(record["birth_country"].items()) if record.get("birth_country") else {}
        cat_props["current_country"] = (
            dict(record["current_country"].items()) if record.get("current_country") else {}
        )
        cat_props["cattery"] = dict(record["cattery"].items()) if record.get("cattery") else {}
        cat_props["source_db"] = dict(record["source_db"].items()) if record.get("source_db") else {}

        return cat_props
