import psycopg2
from neo4j import GraphDatabase

from src.utils import load_config


class DatabaseConnector:
    """
    Class to handle database connections for both PostgreSQL and Neo4j.

    This class manages connection lifecycle and provides standardized
    connection interfaces for testing.
    """

    def __init__(self):
        """Initialize database connector without creating connections."""
        self.config = load_config()
        self.pg_conn = None
        self.neo4j_driver = None

    def connect_postgres(self):
        """
        Connect to PostgreSQL database.

        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            pg_config = self.config.get("relational_database")
            self.pg_conn = psycopg2.connect(
                host=pg_config.get("host"),
                port=pg_config.get("port"),
                database=pg_config.get("dbname"),
                user=pg_config.get("user"),
                password=pg_config.get("password"),
            )
            return True
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return False

    def connect_neo4j(self):
        """
        Connect to Neo4j database.

        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            neo4j_config = self.config.get("graph_database")
            host = neo4j_config.get("host")
            port = neo4j_config.get("port")
            user = neo4j_config.get("user")
            password = neo4j_config.get("password")

            uri = f"bolt://{host}:{port}"
            self.neo4j_driver = GraphDatabase.driver(uri, auth=(user, password))

            with self.neo4j_driver.session() as session:
                result = session.run("RETURN 1")
                result.single()

            return True
        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")
            return False

    def get_postgres_connection(self):
        """Get PostgreSQL connection, connecting if necessary."""
        if not self.pg_conn:
            self.connect_postgres()
        return self.pg_conn

    def get_neo4j_driver(self):
        """Get Neo4j driver, connecting if necessary."""
        if not self.neo4j_driver:
            self.connect_neo4j()
        return self.neo4j_driver

    def close(self):
        """Close all open database connections."""
        if self.pg_conn:
            try:
                self.pg_conn.close()
            except Exception as e:
                print(f"Error closing PostgreSQL connection: {e}")

        if self.neo4j_driver:
            try:
                self.neo4j_driver.close()
            except Exception as e:
                print(f"Error closing Neo4j driver: {e}")

    def __del__(self):
        """Destructor to ensure connections are closed on garbage collection."""
        self.close()
