import os
from pathlib import Path

import pandas as pd
from base_tester import BaseDataIntegrityTester, query_neo4j
from termcolor import colored
from tqdm import tqdm

from src.utils import custom_print, load_data_config


class RelationshipTester(BaseDataIntegrityTester):
    """
    Specialized tester for relationships between nodes.
    Tests the integrity of all relationship types in the cat graph database.
    """

    def __init__(self, driver):
        """
        Initialize the relationship tester with a Neo4j driver and load reference data.

        :param driver: Neo4j driver object
        """
        super().__init__(driver)

    def load_cats(self, columns: list) -> pd.DataFrame:
        """
        Load cat data from CSV file.

        :param columns: List of columns to load from the CSV file
        :return: DataFrame containing cat data
        """
        try:
            data_paths, column_types = load_data_config()
            data_path_final = Path(data_paths["final"])
            csv_path = data_path_final / "cats.csv"
            cats_data = pd.read_csv(csv_path, dtype=column_types, usecols=columns, low_memory=False)
            return cats_data
        except Exception as e:
            custom_print(f"Error loading reference data: {e}", level=2)
            return pd.DataFrame()

    def load_reference_data(self, csv_name: str) -> pd.DataFrame:
        """
        Load reference data from CSV file.

        :param csv_name: Name of the CSV file to load
        :return: DataFrame containing reference data
        """
        try:
            csv_path = os.path.join("data", "final_data", csv_name)
            csv_data = pd.read_csv(csv_path, low_memory=False)
            return csv_data
        except Exception as e:
            custom_print(f"Error loading reference data: {e}", level=2)
            return pd.DataFrame()

    def load_relationship_data_neo4j(self, query: str, rel: str, batch_size: int = 50000) -> pd.DataFrame:
        """
        Load relationship data from Neo4j in batches with progress tracking.

        :param query: Cypher query to execute
        :param rel: Type of relationship to load
        :param batch_size: Size of each batch
        :return: DataFrame with relationship data
        """
        count_query = query.split("RETURN")[0] + "RETURN COUNT(*) AS total"
        total_records = query_neo4j(self.driver, count_query)[0]["total"]

        skip = 0
        all_data = []

        with tqdm(total=total_records, desc=f"Loading {rel} data", unit="records") as pbar:
            while True:
                batch_query = f"{query} SKIP {skip} LIMIT {batch_size}"
                batch_data = query_neo4j(self.driver, batch_query)

                if not batch_data:
                    break

                all_data.extend(batch_data)
                skip += batch_size

                pbar.update(len(batch_data))

        return pd.DataFrame(all_data) if all_data else pd.DataFrame()

    def test_parent_relationships(self) -> bool:
        """
        Tests HAS_FATHER and HAS_MOTHER relationships.

        :return: True if test passes, False otherwise
        """
        custom_print("Testing parent relationships integrity (HAS_FATHER, HAS_MOTHER)")

        father_query = """
        MATCH (c:Cat)
        OPTIONAL MATCH (c)-[r:HAS_FATHER]->(f:Cat)
        RETURN c.id as cat_id, COALESCE(f.id, -1) as father_id
        """
        father_df = self.load_relationship_data_neo4j(father_query, "HAS_FATHER")

        mother_query = """
        MATCH (c:Cat)
        OPTIONAL MATCH (c)-[r:HAS_MOTHER]->(m:Cat)
        RETURN c.id as cat_id, COALESCE(m.id, -1) as mother_id
        """
        mother_df = self.load_relationship_data_neo4j(mother_query, "HAS_MOTHER")

        if father_df.empty or mother_df.empty:
            custom_print("Some relationships not found in Neo4j.", level=2)
            return False

        columns = ["id", "father_id", "mother_id"]
        ref_data = self.load_cats(columns=columns)
        ref_data = ref_data.rename(columns={"id": "cat_id"})

        if ref_data.empty:
            custom_print("CSV reference data is empty, cannot test relationships", level=2)
            return False

        father_match = True
        father_df_set = set(zip(father_df["cat_id"], father_df["father_id"]))
        ref_father_set = set(zip(ref_data["cat_id"], ref_data["father_id"]))

        match = father_df_set == ref_father_set
        if not match:
            custom_print(colored("Father relationship test failed.", "red"), level=2)
            missing = ref_father_set - father_df_set
            extra = father_df_set - ref_father_set
            if missing:
                custom_print(colored(f"Missing father relationships: {len(missing)}", "yellow"), level=2)
            if extra:
                custom_print(colored(f"Extra father relationships: {len(extra)}", "yellow"), level=2)

        mother_match = True
        mother_df_set = set(zip(mother_df["cat_id"], mother_df["mother_id"]))
        ref_mother_set = set(zip(ref_data["cat_id"], ref_data["mother_id"]))

        match = mother_df_set == ref_mother_set
        if not match:
            custom_print(colored("Mother relationship test failed.", "red"), level=2)
            missing = ref_mother_set - mother_df_set
            extra = mother_df_set - ref_mother_set
            if missing:
                custom_print(colored(f"Missing mother relationships: {len(missing)}", "yellow"), level=2)
            if extra:
                custom_print(colored(f"Extra mother relationships: {len(extra)}", "yellow"), level=2)

        result = father_match and mother_match
        if result:
            print(colored("Parent relationships integrity test passed.", "green"))

        return result

    def test_cat_breed_relationship(self) -> bool:
        """
        Tests relationship integrity between cats and breeds (BELONGS_TO_BREED).

        :return: True if test passes, False otherwise
        """
        custom_print("Testing Cat-Breed relationships integrity (BELONGS_TO_BREED)")
        query = """
        MATCH (c:Cat)-[r:BELONGS_TO_BREED]->(b:Breed)
        RETURN c.id as cat_id, b.breed_code as breed_code
        """
        neo_df = self.load_relationship_data_neo4j(query, "BELONGS_TO_BREED")

        if neo_df.empty:
            custom_print(
                colored("Breed relationship test failed. No relationships found in Neo4j.", "red"), level=2
            )
            return False

        cats_df = self.load_cats(columns=["id", "breed_code_id"])
        breeds_df = self.load_reference_data(csv_name="breeds.csv")
        if cats_df.empty or breeds_df.empty:
            custom_print("CSV reference data is empty, cannot test relationships", level=2)
            return False

        cats_df = cats_df.rename(columns={"id": "cat_id"})
        ref_data = cats_df.merge(breeds_df, left_on="breed_code_id", right_on="id", how="inner")
        ref_data = ref_data.drop(columns=["id", "breed_code_id"])
        del cats_df, breeds_df

        neo_df_set = set(zip(neo_df["cat_id"], neo_df["breed_code"]))
        ref_data_set = set(zip(ref_data["cat_id"], ref_data["breed_code"]))

        match = neo_df_set == ref_data_set

        if match:
            print(colored("Breed relationship integrity test passed.", "green"))
        else:
            custom_print(colored("Breed relationship integrity test failed.", "red"), level=2)
            missing = ref_data_set - neo_df_set
            extra = neo_df_set - ref_data_set
            if missing:
                custom_print(colored(f"Missing breed relationships: {len(missing)}", "yellow"), level=2)
            if extra:
                custom_print(colored(f"Extra breed relationships: {len(extra)}", "yellow"), level=2)

        return match

    def test_cat_color_relationship(self) -> bool:
        """
        Tests relationship integrity between cats and colors (HAS_COLOR).

        :return: True if test passes, False otherwise
        """
        custom_print("Testing Cat-Color relationships integrity (HAS_COLOR)")

        query = """
        MATCH (c:Cat)-[r:HAS_COLOR]->(col:Color)
        RETURN c.id as cat_id, col.breed_code as breed_code, col.color_code as color_code, 
            col.color_definition as color_definition, col.full_breed_name as full_breed_name,
            col.breed_group as breed_group, col.breed_category as breed_category
        """
        neo_df = self.load_relationship_data_neo4j(query, "HAS_COLOR")

        if neo_df.empty:
            custom_print(
                colored("Color relationship test failed. No relationships found in Neo4j.", "red"), level=2
            )
            return False

        cats_df = self.load_cats(columns=["id", "color_id"])
        colors_df = self.load_reference_data(csv_name="colors.csv")
        if cats_df.empty or colors_df.empty:
            custom_print("CSV reference data is empty, cannot test relationships", level=2)
            return False

        cats_df = cats_df.rename(columns={"id": "cat_id"})
        ref_data = cats_df.merge(colors_df, left_on="color_id", right_on="id")
        ref_data = ref_data.drop(columns=["id", "color_id", "full_breed_name", "breed_group", "breed_category"])

        neo_df_set = set(
            zip(neo_df["cat_id"], neo_df["breed_code"], neo_df["color_code"], neo_df["color_definition"])
        )
        ref_data_set = set(
            zip(ref_data["cat_id"], ref_data["breed_code"], ref_data["color_code"], ref_data["color_definition"])
        )

        match = neo_df_set == ref_data_set

        if match:
            print(colored("Color relationship integrity test passed.", "green"))
        else:
            custom_print(colored("Color relationship integrity test failed.", "red"), level=2)
            missing = ref_data_set - neo_df_set
            extra = neo_df_set - ref_data_set
            if missing:
                custom_print(colored(f"Missing color relationships: {len(missing)}", "yellow"), level=2)
            if extra:
                custom_print(colored(f"Extra color relationships: {len(extra)}", "yellow"), level=2)

        return match

    def test_cat_country_relationships(self) -> bool:
        """
        Tests relationship integrity between cats and countries (BORN_IN, LIVES_IN).

        :return: True if test passes, False otherwise
        """
        custom_print("Testing Cat-Country relationships integrity (BORN_IN, LIVES_IN)")

        origin_query = """
        MATCH (c:Cat)-[r:BORN_IN]->(co:Country)
        RETURN c.id as cat_id, co.alpha_3 as country_code, co.country_name as country_name
        """
        origin_df = self.load_relationship_data_neo4j(origin_query, "BORN_IN")

        if origin_df.empty:
            custom_print(
                colored("Origin country relationship test failed. No relationships found in Neo4j.", "red"),
                level=2,
            )
            return False

        current_query = """
        MATCH (c:Cat)-[r:LIVES_IN]->(co:Country)
        RETURN c.id as cat_id, co.alpha_3 as country_code, co.country_name as country_name
        """
        current_df = self.load_relationship_data_neo4j(current_query, "LIVES_IN")

        if current_df.empty:
            custom_print(
                colored("Current country relationship test failed. No relationships found in Neo4j.", "red"),
                level=2,
            )
            return False

        cats_df = self.load_cats(columns=["id", "country_origin_id", "country_current_id"])
        countries_df = self.load_reference_data(csv_name="countries.csv")
        if cats_df.empty or countries_df.empty:
            custom_print("CSV reference data is empty, cannot test relationships", level=2)
            return False

        cats_df = cats_df.rename(columns={"id": "cat_id"})
        countries_df = countries_df.dropna(subset=["alpha_2", "iso_numeric"])
        countries_df = countries_df.rename(columns={"id": "country_id", "alpha_3": "country_code"})

        ref_origin = cats_df.merge(countries_df, left_on="country_origin_id", right_on="country_id")
        ref_origin = ref_origin.drop(
            columns=["country_origin_id", "country_current_id", "country_id", "alpha_2", "iso_numeric"]
        )

        ref_current = cats_df.merge(countries_df, left_on="country_current_id", right_on="country_id")
        ref_current = ref_current.drop(
            columns=["country_origin_id", "country_current_id", "country_id", "alpha_2", "iso_numeric"]
        )

        del cats_df, countries_df

        origin_df_set = set(zip(origin_df["cat_id"], origin_df["country_code"], origin_df["country_name"]))
        ref_origin_set = set(zip(ref_origin["cat_id"], ref_origin["country_code"], ref_origin["country_name"]))

        origin_match = origin_df_set == ref_origin_set
        if not origin_match:
            custom_print(colored("Origin country relationship test failed.", "red"), level=2)
            missing = ref_origin_set - origin_df_set
            extra = origin_df_set - ref_origin_set
            if missing:
                custom_print(colored(f"Missing origin country relationships: {len(missing)}", "yellow"), level=2)
            if extra:
                custom_print(colored(f"Extra origin country relationships: {len(extra)}", "yellow"), level=2)

        current_df_set = set(zip(current_df["cat_id"], current_df["country_code"], current_df["country_name"]))
        ref_current_set = set(zip(ref_current["cat_id"], ref_current["country_code"], ref_current["country_name"]))

        current_match = current_df_set == ref_current_set
        if not current_match:
            custom_print(colored("Current country relationship test failed.", "red"), level=2)
            missing = ref_current_set - current_df_set
            extra = current_df_set - ref_current_set
            if missing:
                custom_print(colored(f"Missing current country relationships: {len(missing)}", "yellow"), level=2)
            if extra:
                custom_print(colored(f"Extra current country relationships: {len(extra)}", "yellow"), level=2)

        result = origin_match and current_match
        if result:
            print(colored("Country relationships integrity test passed.", "green"))

        return result

    def test_cat_cattery_relationship(self) -> bool:
        """
        Tests relationship integrity between cats and catteries (BRED_BY).

        :return: True if test passes, False otherwise
        """
        custom_print("Testing Cat-Cattery relationships integrity (BRED_BY)")

        query = """
        MATCH (c:Cat)-[r:BRED_BY]->(ct:Cattery)
        RETURN c.id as cat_id, ct.cattery_name as cattery_name
        """
        rel_df = self.load_relationship_data_neo4j(query, "BRED_BY")

        if rel_df.empty:
            custom_print(
                colored("Cattery relationship test failed. No relationships found in Neo4j.", "red"), level=2
            )
            return False

        cats_df = self.load_cats(columns=["id", "cattery_id"])
        catteries_df = self.load_reference_data(csv_name="catteries.csv")
        if cats_df.empty or catteries_df.empty:
            custom_print("CSV reference data is empty, cannot test relationships", level=2)
            return False

        cats_df = cats_df.rename(columns={"id": "cat_id"})
        ref_data = cats_df.merge(catteries_df, left_on="cattery_id", right_on="id")
        ref_data = ref_data.drop(columns=["cattery_id", "id"])

        del cats_df, catteries_df

        rel_df_set = set(zip(rel_df["cat_id"], rel_df["cattery_name"]))
        ref_cattery_set = set(zip(ref_data["cat_id"], ref_data["cattery_name"]))

        match = rel_df_set == ref_cattery_set

        if match:
            print(colored("Cattery relationship integrity test passed.", "green"))
        else:
            custom_print(colored("Cattery relationship integrity test failed.", "red"), level=2)
            missing = ref_cattery_set - rel_df_set
            extra = rel_df_set - ref_cattery_set
            if missing:
                custom_print(colored(f"Missing cattery relationships: {len(missing)}", "yellow"), level=2)
            if extra:
                custom_print(colored(f"Extra cattery relationships: {len(extra)}", "yellow"), level=2)

        return match

    def test_cat_source_db_relationship(self) -> bool:
        """
        Tests relationship integrity between cats and source databases (FROM_DATABASE).

        :return: True if test passes, False otherwise
        """
        custom_print("Testing Cat-SourceDB relationships integrity (FROM_DATABASE)")

        query = """
        MATCH (c:Cat)-[r:FROM_DATABASE]->(s:SourceDB)
        RETURN c.id as cat_id, s.source_db_name as source_db_name
        """
        neo_df = self.load_relationship_data_neo4j(query, "FROM_DATABASE")

        if neo_df.empty:
            custom_print(
                colored("Source DB relationship test failed. No relationships found in Neo4j.", "red"), level=2
            )
            return False

        cats_df = self.load_cats(columns=["id", "source_db_id"])
        ref_data = self.load_reference_data(csv_name="source_dbs.csv")
        if cats_df.empty or ref_data.empty:
            custom_print("CSV reference data is empty, cannot test relationships", level=2)
            return False

        cats_df = cats_df.rename(columns={"id": "cat_id"})
        ref_data = cats_df.merge(ref_data, left_on="source_db_id", right_on="id")
        ref_data = ref_data.drop(columns=["id", "source_db_id"])

        neo_df_set = set(zip(neo_df["cat_id"], neo_df["source_db_name"]))
        ref_data_set = set(zip(ref_data["cat_id"], ref_data["source_db_name"]))

        match = neo_df_set == ref_data_set

        if match:
            print(colored("Source DB relationship integrity test passed.", "green"))
        else:
            custom_print(colored("Source DB relationship integrity test failed.", "red"), level=2)
            missing = ref_data_set - neo_df_set
            extra = neo_df_set - ref_data_set
            if missing:
                custom_print(colored(f"Missing source DB relationships: {len(missing)}", "yellow"), level=2)
            if extra:
                custom_print(colored(f"Extra source DB relationships: {len(extra)}", "yellow"), level=2)

        return match

    def test_all_relationships(self) -> dict:
        """
        Tests all relationship types in the database.

        :return: Dictionary with test results for all relationship types
        """

        parent_result = self.test_parent_relationships()
        breed_result = self.test_cat_breed_relationship()
        color_result = self.test_cat_color_relationship()
        country_result = self.test_cat_country_relationships()
        cattery_result = self.test_cat_cattery_relationship()
        source_db_result = self.test_cat_source_db_relationship()

        return {
            "Parent Relationships": parent_result,
            "Breed Relationships": breed_result,
            "Color Relationships": color_result,
            "Country Relationships": country_result,
            "Cattery Relationships": cattery_result,
            "Source DB Relationships": source_db_result,
        }
