class TestConfig:
    """
    Configuration for performance testing.

    Defines test parameters like cat IDs, depths, and iterations.
    """

    DEFAULT_CAT_ID = 2

    DEPTH_TIERS = [
        {"depths": [1, 2, 3, 4, 5], "iterations": 50},
        {"depths": [6, 7, 8, 9, 10], "iterations": 25},
        {"depths": [20, 50], "iterations": 10},
        {"depths": [100, 500, 1000], "iterations": 2},
    ]
    NON_DEPTH_ITERATIONS = 10

    """ DEPTH_TIERS = [
        {"depths": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "iterations": 100},
        {"depths": [20, 50, 100], "iterations": 25},
        {"depths": [500, 1000], "iterations": 10},
    ]
    NON_DEPTH_ITERATIONS = 100 """

    QUERY_TYPES = ["tree_ancestry", "tree_all", "breed_distribution"]
    DEPTH_QUERY_TYPES = ["tree_ancestry", "tree_all"]

    @classmethod
    def get_test_cases(cls):
        """
        Generate all test cases based on configuration.

        Returns:
            list: List of dictionaries with test case parameters
        """
        test_cases = []

        for query_type in cls.DEPTH_QUERY_TYPES:
            for tier in cls.DEPTH_TIERS:
                iterations = tier["iterations"]
                for depth in tier["depths"]:
                    test_cases.append(
                        {
                            "query_type": query_type,
                            "cat_id": cls.DEFAULT_CAT_ID,
                            "depth": depth,
                            "iterations": iterations,
                        }
                    )

        for query_type in set(cls.QUERY_TYPES) - set(cls.DEPTH_QUERY_TYPES):
            test_cases.append(
                {
                    "query_type": query_type,
                    "cat_id": cls.DEFAULT_CAT_ID,
                    "depth": 1,
                    "iterations": cls.NON_DEPTH_ITERATIONS,
                }
            )

        return test_cases
