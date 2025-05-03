import sys
from datetime import datetime
from pathlib import Path

from termcolor import colored
from test_framework import run_performance_tests

script_dir = Path(__file__).parent
project_dir = script_dir.parent.parent


def ensure_output_directories():
    """Create output directories if they don't exist."""
    output_dir = project_dir / "output"
    if not output_dir.exists():
        print(f"Creating main output directory: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    test_output_dir = output_dir / f"test_results_{timestamp}"

    query_types = ["tree_all", "tree_ancestry", "breed_distribution"]

    print("Creating test output directories:")
    print(f"  - {test_output_dir}")

    for query_type in query_types:
        query_dir = test_output_dir / query_type
        print(f"  - {query_dir}")
        query_dir.mkdir(parents=True, exist_ok=True)

    return str(test_output_dir)


def main():
    """Run all the configured tests."""
    print(colored("\n==================================", "yellow"))
    print(colored("  STARTING DATABASE PERFORMANCE TESTING", "yellow"))
    print(colored("==================================\n", "yellow"))

    ensure_output_directories()

    try:
        output_path = run_performance_tests()

        print(colored("\n==================================", "green"))
        print(colored("  TESTING COMPLETED SUCCESSFULLY  ", "green"))
        print(colored("==================================\n", "green"))
        print(f"Results are available at: {colored(output_path, 'blue')}")
        return 0

    except KeyboardInterrupt:
        print(colored("\nTests interrupted by user. Partial results may be available.", "yellow"))
        return 1
    except Exception as e:
        print(colored(f"\nError during testing: {e}", "red"))
        return 1


if __name__ == "__main__":
    sys.exit(main())
