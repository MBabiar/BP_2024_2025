import sys
import time
from pathlib import Path

import polars as pl
from neo4j import GraphDatabase, basic_auth
from tqdm import tqdm

from src.utils import custom_print, is_running_in_docker, load_config, load_data_config

BATCH_SIZE = 25000


def load_batch_size():
    """
    Loads the batch size from config.json and sets it as a global variable.
    """
    global BATCH_SIZE
    config = load_config()
    try:
        BATCH_SIZE = config.get("batch_size", BATCH_SIZE)
        custom_print(f"Batch size set to: {BATCH_SIZE}", level=2)
    except Exception as e:
        print(f"Error loading batch size: {e}")
        sys.exit(1)


def connect_to_neo4j():
    """
    Connect to Neo4j database using credentials from config.json with retries and ensure complete database cleanup
    """
    custom_print("Connecting to Neo4j database")
    retries = 30

    is_docker = is_running_in_docker()
    config = load_config()
    try:
        config_key = "graph_database_docker" if is_docker else "graph_database"

        neo4j_config = config.get(config_key)
        host = neo4j_config.get("host")
        port = neo4j_config.get("port")
        username = neo4j_config.get("user")
        password = neo4j_config.get("password")

        uri = f"bolt://{host}:{port}"
    except Exception as e:
        print(f"Error loading Neo4j configuration: {e}")
        sys.exit(1)

    for attempt in range(retries):
        try:
            driver = GraphDatabase.driver(uri, auth=basic_auth(username, password))

            with driver.session() as session:
                session.run("MATCH (n) RETURN COUNT(n) LIMIT 1")

            custom_print("Connected to Neo4j database successfully!", level=2)
            return driver
        except Exception as e:
            if attempt < 10:
                time.sleep(2)
            elif attempt < retries - 1:
                print(f"Connection attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(2)
            else:
                print(f"Error connecting to Neo4j after {retries} attempts: {e}")
                sys.exit(1)


def load_csv(file_name):
    """
    Load and return CSV data as a polars DataFrame from final_data directory
    """
    data_paths, config = load_data_config()
    data_path_final = Path(data_paths["final"])
    file_path = data_path_final / file_name
    try:
        df = pl.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading CSV {file_name}: {e}")
        sys.exit(1)


def create_cat_nodes(driver, cats_df):
    """
    Create cat nodes from cats.csv using batch processing with UNWIND
    """
    total_cats = cats_df.height

    with driver.session() as session:
        with tqdm(total=total_cats, desc="Creating cat nodes") as pbar:
            for i in range(0, total_cats, BATCH_SIZE):
                batch_df = cats_df.slice(i, min(BATCH_SIZE, total_cats - i))
                batch_size_actual = batch_df.height

                batch_data = []
                for row_idx in range(batch_df.height):
                    batch_data.append(batch_df.row(row_idx, named=True))

                session.run(
                    """
                    UNWIND $batch AS row
                    CREATE (c:Cat {
                        id: row.id,
                        name: row.name,
                        date_of_birth: row.date_of_birth,
                        gender: row.gender,
                        registration_number_current: row.registration_number_current,
                        title_before: row.title_before,
                        title_after: row.title_after,
                        chip: row.chip
                    })
                    """,
                    batch=batch_data,
                )

                pbar.update(batch_size_actual)

    return cats_df["id"].to_list()


def create_breed_nodes(driver, breed_df):
    """
    Create breed nodes from breed.csv using batch processing with UNWIND
    """
    total_breeds = breed_df.height

    with driver.session() as session:
        with tqdm(total=total_breeds, desc="Creating breed nodes") as pbar:
            for i in range(0, total_breeds, BATCH_SIZE):
                batch_df = breed_df.slice(i, min(BATCH_SIZE, total_breeds - i))
                batch_size_actual = batch_df.height

                batch_data = []
                for row_idx in range(batch_df.height):
                    batch_data.append(breed_df.row(row_idx + i, named=True))

                session.run(
                    """
                    UNWIND $batch AS row
                    CREATE (b:Breed {
                        id: row.id,
                        breed_code: row.breed_code,
                        breed_full_name: row.breed_full_name
                    })
                    """,
                    batch=batch_data,
                )

                pbar.update(batch_size_actual)

    return breed_df["id"].to_list()


def create_color_nodes(driver, color_df):
    """
    Create color nodes from color.csv using batch processing with UNWIND
    """
    total_colors = color_df.height

    with driver.session() as session:
        with tqdm(total=total_colors, desc="Creating color nodes") as pbar:
            for i in range(0, total_colors, BATCH_SIZE):
                batch_df = color_df.slice(i, min(BATCH_SIZE, total_colors - i))
                batch_size_actual = batch_df.height

                batch_data = []
                for row_idx in range(batch_df.height):
                    batch_data.append(color_df.row(row_idx + i, named=True))

                session.run(
                    """
                    UNWIND $batch AS row
                    CREATE (c:Color {
                        id: row.id,
                        breed_code: row.breed_code,
                        color_code: row.color_code,
                        color_definition: row.color_definition,
                        full_breed_name: row.full_breed_name,
                        breed_group: row.breed_group,
                        breed_category: row.breed_category
                    })
                    """,
                    batch=batch_data,
                )

                pbar.update(batch_size_actual)

    return color_df["id"].to_list()


def create_country_nodes(driver, country_df):
    """
    Create country nodes from country.csv using batch processing with UNWIND
    """
    total_countries = country_df.height

    with driver.session() as session:
        with tqdm(total=total_countries, desc="Creating country nodes") as pbar:
            for i in range(0, total_countries, BATCH_SIZE):
                batch_df = country_df.slice(i, min(BATCH_SIZE, total_countries - i))
                batch_size_actual = batch_df.height

                batch_data = []
                for row_idx in range(batch_df.height):
                    batch_data.append(country_df.row(row_idx + i, named=True))

                session.run(
                    """
                    UNWIND $batch AS row
                    CREATE (c:Country {
                        id: row.id,
                        country_name: row.country_name,
                        alpha_2: row.alpha_2,
                        alpha_3: row.alpha_3,
                        iso_numeric: row.iso_numeric
                    })
                    """,
                    batch=batch_data,
                )

                pbar.update(batch_size_actual)

    return country_df["id"].to_list()


def create_cattery_nodes(driver, cattery_df):
    """
    Create cattery nodes from cattery.csv using batch processing with UNWIND
    """
    total_catteries = cattery_df.height

    with driver.session() as session:
        with tqdm(total=total_catteries, desc="Creating cattery nodes") as pbar:
            for i in range(0, total_catteries, BATCH_SIZE):
                batch_df = cattery_df.slice(i, min(BATCH_SIZE, total_catteries - i))
                batch_size_actual = batch_df.height

                batch_data = []
                for row_idx in range(batch_df.height):
                    batch_data.append(cattery_df.row(row_idx + i, named=True))

                session.run(
                    """
                    UNWIND $batch AS row
                    CREATE (c:Cattery {
                        id: row.id,
                        cattery_name: row.cattery_name
                    })
                    """,
                    batch=batch_data,
                )

                pbar.update(batch_size_actual)

    return cattery_df["id"].to_list()


def create_source_db_nodes(driver, src_db_df):
    """
    Create source database nodes from src_db.csv using batch processing with UNWIND
    """
    total_dbs = src_db_df.height

    with driver.session() as session:
        with tqdm(total=total_dbs, desc="Creating source database nodes") as pbar:
            for i in range(0, total_dbs, BATCH_SIZE):
                batch_df = src_db_df.slice(i, min(BATCH_SIZE, total_dbs - i))
                batch_size_actual = batch_df.height

                batch_data = []
                for row_idx in range(batch_df.height):
                    batch_data.append(src_db_df.row(row_idx + i, named=True))

                session.run(
                    """
                    UNWIND $batch AS row
                    CREATE (s:SourceDB {
                        id: row.id,
                        source_db_name: row.source_db_name
                    })
                    """,
                    batch=batch_data,
                )

                pbar.update(batch_size_actual)

    return src_db_df["id"].to_list()


def create_indexes(driver):
    """
    Create indexes for faster lookups on various node types in the database.
    """
    index_queries = [
        ("Cat", "cat_id_index", "id"),
        ("Breed", "breed_id_index", "id"),
        ("Color", "color_id_index", "id"),
        ("Country", "country_id_index", "id"),
        ("Cattery", "cattery_id_index", "id"),
        ("SourceDB", "src_db_id_index", "id"),
    ]

    with driver.session() as session:
        for label, index_name, property_name in index_queries:
            session.run(f"CREATE INDEX {index_name} FOR (n:{label}) ON (n.{property_name})")
            print(f"Index '{index_name}' for '{label}' on property '{property_name}' created")

        session.run("CREATE FULLTEXT INDEX cat_name_fulltext FOR (n:Cat) ON EACH [n.name]")


def create_parent_relationships(driver, cats_df):
    """
    Create parent relationships based on cats.csv
    """
    father_rels = []
    mother_rels = []

    for row in cats_df.iter_rows(named=True):
        cat_id = row["id"]
        father_id = row.get("father_id")
        mother_id = row.get("mother_id")

        if father_id is not None and father_id != -1:
            father_rels.append({"father": father_id, "child": cat_id})

        if mother_id is not None and mother_id != -1:
            mother_rels.append({"mother": mother_id, "child": cat_id})

    with driver.session() as session:
        total_fathers = len(father_rels)
        with tqdm(total=total_fathers, desc="Creating HAS_FATHER relationships") as pbar:
            for i in range(0, len(father_rels), BATCH_SIZE):
                batch = father_rels[i : i + BATCH_SIZE]
                batch_size_actual = len(batch)

                session.run(
                    """
                    UNWIND $batch AS row
                    MATCH (father:Cat {id: row.father}), (child:Cat {id: row.child})
                    CREATE (child)-[:HAS_FATHER]->(father)
                    """,
                    batch=batch,
                )

                pbar.update(batch_size_actual)

        total_mothers = len(mother_rels)
        with tqdm(total=total_mothers, desc="Creating HAS_MOTHER relationships") as pbar:
            for i in range(0, len(mother_rels), BATCH_SIZE):
                batch = mother_rels[i : i + BATCH_SIZE]
                batch_size_actual = len(batch)

                session.run(
                    """
                    UNWIND $batch AS row
                    MATCH (mother:Cat {id: row.mother}), (child:Cat {id: row.child})
                    CREATE (child)-[:HAS_MOTHER]->(mother)
                    """,
                    batch=batch,
                )

                pbar.update(batch_size_actual)


def create_entity_relationships(driver, cats_df):
    """
    Create relationships between cats and other entities.
    """
    relationships = [
        {"column": "breed_code_id", "node_type": "Breed", "rel_type": "BELONGS_TO_BREED"},
        {"column": "color_id", "node_type": "Color", "rel_type": "HAS_COLOR"},
        {"column": "country_origin_id", "node_type": "Country", "rel_type": "BORN_IN"},
        {"column": "country_current_id", "node_type": "Country", "rel_type": "LIVES_IN"},
        {"column": "cattery_id", "node_type": "Cattery", "rel_type": "BRED_BY"},
        {"column": "source_db_id", "node_type": "SourceDB", "rel_type": "FROM_DATABASE"},
    ]

    with driver.session() as session:
        for rel_info in relationships:
            column = rel_info["column"]
            node_type = rel_info["node_type"]
            rel_type = rel_info["rel_type"]

            relationships = []
            for row in cats_df.iter_rows(named=True):
                cat_id = row["id"]
                entity_id = row.get(column)

                if entity_id is not None:
                    relationships.append({"cat_id": cat_id, "entity_id": entity_id})

            total_rels = len(relationships)
            with tqdm(total=total_rels, desc=f"Creating {rel_type} relationships") as pbar:
                for i in range(0, total_rels, BATCH_SIZE):
                    batch = relationships[i : i + BATCH_SIZE]
                    batch_size_actual = len(batch)

                    session.run(
                        f"""
                        UNWIND $batch AS row
                        MATCH (c:Cat {{id: row.cat_id}}), (e:{node_type} {{id: row.entity_id}})
                        CREATE (c)-[:{rel_type}]->(e)
                        """,
                        batch=batch,
                    )

                    pbar.update(batch_size_actual)


def main():
    custom_print("Loading Batch Size")
    load_batch_size()

    driver = connect_to_neo4j()

    custom_print("Loading data from CSV files")
    cats_df = load_csv("cats.csv")
    breed_df = load_csv("breeds.csv")
    color_df = load_csv("colors.csv")
    country_df = load_csv("countries.csv")
    cattery_df = load_csv("catteries.csv")
    src_db_df = load_csv("source_dbs.csv")
    custom_print("Data loaded successfully!", level=2)

    try:
        custom_print("Creating nodes")
        create_cat_nodes(driver, cats_df)
        create_breed_nodes(driver, breed_df)
        create_color_nodes(driver, color_df)
        create_country_nodes(driver, country_df)
        create_cattery_nodes(driver, cattery_df)
        create_source_db_nodes(driver, src_db_df)

        custom_print("Creating indexes")
        create_indexes(driver)

        custom_print("Creating relationships")
        create_parent_relationships(driver, cats_df)
        create_entity_relationships(driver, cats_df)

        custom_print("Graph database populated successfully!")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
