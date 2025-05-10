import os
import time

from termcolor import colored

from .performance_tester import PerformanceTester
from .results_logger import ResultsLogger
from .test_config import TestConfig


def run_performance_tests(output_dir=None):
    """
    Run performance tests comparing Neo4j and PostgreSQL.

    Args:
        output_dir (str, optional): Path to an existing output directory. If None, creates a new one.

    Returns:
        str: Path to the output directory
    """
    cat_id = TestConfig.DEFAULT_CAT_ID

    print(
        colored(f"\n{'=' * 80}\n  PERFORMANCE TEST: Neo4j vs PostgreSQL Family tree Queries\n{'=' * 80}", "yellow")
    )
    print(f"Testing with cat ID: {cat_id}")

    tester = PerformanceTester()
    logger = ResultsLogger(output_dir=output_dir)

    print(f"Results will be saved to: {colored(logger.output_dir, 'green')}")

    os.makedirs(logger.output_dir, exist_ok=True)

    test_cases = TestConfig.get_test_cases()

    total_tests = len(test_cases)
    for i, test_case in enumerate(test_cases, 1):
        query_type = test_case["query_type"]
        depth = test_case["depth"]
        iterations = test_case["iterations"]

        print(f"\n{'-' * 60}")
        print(
            colored(
                f"Test {i}/{total_tests}: query_type={query_type}, depth={depth}, iterations={iterations}", "cyan"
            )
        )

        start_time = time.time()
        result = tester.run_test(query_type=query_type, cat_id=cat_id, depth=depth, iterations=iterations)
        end_time = time.time()

        logger.save_test_result(result)

        pg_avg = result["postgres"]["avg"]
        neo_avg = result["neo4j"]["avg"]
        winner = result["winner"]
        factor = result["factor"]

        print(f"PostgreSQL avg: {colored(f'{pg_avg:.2f}ms', 'blue')}")
        print(f"Neo4j avg: {colored(f'{neo_avg:.2f}ms', 'green')}")
        print(f"Winner: {colored(winner, 'green' if winner == 'Neo4j' else 'blue')} ({factor:.2f}x faster)")
        print(f"Test completed in {end_time - start_time:.2f} seconds")

    logger.save_summary()
    tester.cleanup()

    print(f"\n{'-' * 60}")
    print(colored("All tests completed!", "yellow"))
    print(f"Summary files saved to: {colored(logger.output_dir, 'green')}")

    return str(logger.output_dir)


if __name__ == "__main__":
    run_performance_tests()
