class TestConfig:
    """
    Configuration for performance testing.

    Defines test parameters like cat IDs, depths, and iterations.
    """

    DEFAULT_CAT_ID = 2

    DEPTH_TIERS = [
        {"depths": [3, 5], "iterations": 1000},
        {"depths": [10], "iterations": 500},
        {"depths": [15], "iterations": 100},
        {"depths": [20, 23], "iterations": 50},
    ]
    NON_DEPTH_ITERATIONS = 200

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
