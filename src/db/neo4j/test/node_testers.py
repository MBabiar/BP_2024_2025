from base_tester import BaseDataIntegrityTester


class CatsTester(BaseDataIntegrityTester):
    """
    Specialized tester for Cat nodes.
    """

    def test_integrity(self) -> bool:
        """
        Tests data integrity for Cat nodes.

        :return: True if test passes, False otherwise
        """
        properties = [
            "id",
            "name",
            "date_of_birth",
            "gender",
            "registration_number_current",
            "title_before",
            "title_after",
            "chip",
        ]

        return super().test_integrity("Cat", properties, "cats.csv")


class BreedsTester(BaseDataIntegrityTester):
    """
    Specialized tester for Breed nodes.
    """

    def test_integrity(self) -> bool:
        """
        Tests data integrity for Breed nodes.

        :return: True if test passes, False otherwise
        """
        properties = ["id", "breed_code"]

        return super().test_integrity("Breed", properties, "breeds.csv")


class ColorsTester(BaseDataIntegrityTester):
    """
    Specialized tester for Color nodes.
    """

    def test_integrity(self) -> bool:
        """
        Tests data integrity for Color nodes.

        :return: True if test passes, False otherwise
        """
        properties = [
            "id",
            "breed_code",
            "color_code",
            "color_definition",
            "full_breed_name",
            "breed_group",
            "breed_category",
        ]

        return super().test_integrity("Color", properties, "colors.csv")


class CountriesTester(BaseDataIntegrityTester):
    """
    Specialized tester for Country nodes.
    """

    def test_integrity(self) -> bool:
        """
        Tests data integrity for Country nodes.

        :return: True if test passes, False otherwise
        """
        properties = ["id", "country_name", "alpha_2", "alpha_3", "iso_numeric"]

        return super().test_integrity("Country", properties, "countries.csv")


class CatteriesTester(BaseDataIntegrityTester):
    """
    Specialized tester for Cattery nodes.
    """

    def test_integrity(self) -> bool:
        """
        Tests data integrity for Cattery nodes.

        :return: True if test passes, False otherwise
        """
        properties = ["id", "cattery_name"]

        return super().test_integrity("Cattery", properties, "catteries.csv")


class SourceDatabaseTester(BaseDataIntegrityTester):
    """
    Specialized tester for SourceDatabase nodes.
    """

    def test_integrity(self) -> bool:
        """
        Tests data integrity for SourceDatabase nodes.

        :return: True if test passes, False otherwise
        """
        properties = ["id", "source_db_name"]

        return super().test_integrity("SourceDB", properties, "source_dbs.csv")
