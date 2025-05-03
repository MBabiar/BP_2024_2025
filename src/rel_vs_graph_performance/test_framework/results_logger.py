import csv
import datetime
import json
import os
from pathlib import Path


class ResultsLogger:
    """
    Class to handle saving test results to files.

    Manages test output directory creation and saving results
    in various formats.
    """

    def __init__(self, output_dir=None):
        """
        Initialize the results logger with a timestamped output directory.

        Args:
            output_dir (str, optional): Path to existing output directory. If None, creates a new one.
        """
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        project_root = Path(__file__).parent.parent.parent.parent

        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = project_root / "output" / f"test_results_{self.timestamp}"

        os.makedirs(self.output_dir, exist_ok=True)

        self.tree_ancestry_dir = self.output_dir / "tree_ancestry"
        self.tree_all_dir = self.output_dir / "tree_all"
        self.breed_distribution_dir = self.output_dir / "breed_distribution"

        os.makedirs(self.tree_ancestry_dir, exist_ok=True)
        os.makedirs(self.tree_all_dir, exist_ok=True)
        os.makedirs(self.breed_distribution_dir, exist_ok=True)

        self.tree_ancestry_summary = []
        self.tree_all_summary = []
        self.breed_distribution_summary = []

    def _get_result_dir(self, query_type):
        """Get the appropriate directory for the query type."""
        if query_type == "tree_ancestry":
            return self.tree_ancestry_dir
        elif query_type == "tree_all":
            return self.tree_all_dir
        elif query_type == "breed_distribution":
            return self.breed_distribution_dir
        else:
            return self.output_dir

    def save_test_result(self, result):
        """
        Save detailed test results to a file.

        Args:
            result (dict): Test result data from PerformanceTester
        """
        params = result["params"]
        query_type = params["query_type"]
        depth = params["depth"]
        cat_id = params["cat_id"]

        result_dir = self._get_result_dir(query_type)

        result_file = result_dir / f"cat{cat_id}_depth{depth}.json"

        with open(result_file, "w") as f:
            json.dump(result, f, indent=2)

        self._save_time_measurements(result, result_dir, cat_id, depth)

        summary_entry = {
            "cat_id": cat_id,
            "depth": depth,
            "iterations": params["iterations"],
            "postgres_avg": result["postgres"]["avg"],
            "neo4j_avg": result["neo4j"]["avg"],
            "postgres_median": result["postgres"]["median"],
            "neo4j_median": result["neo4j"]["median"],
            "winner": result["winner"],
            "speed_factor": result["factor"],
        }

        if query_type == "tree_ancestry":
            self.tree_ancestry_summary.append(summary_entry)
        elif query_type == "tree_all":
            self.tree_all_summary.append(summary_entry)
        elif query_type == "breed_distribution":
            self.breed_distribution_summary.append(summary_entry)

    def _save_time_measurements(self, result, result_dir, cat_id, depth):
        """
        Save individual time measurements to CSV files.

        Args:
            result (dict): Test result data
            result_dir (Path): Directory to save files
            cat_id (int): Cat ID
            depth (int): Depth of query
        """
        pg_times_file = result_dir / f"cat{cat_id}_depth{depth}_postgres_times.csv"
        with open(pg_times_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["iteration", "execution_time_seconds"])
            for i, time_val in enumerate(result["postgres"]["times"], 1):
                writer.writerow([i, time_val])

        neo4j_times_file = result_dir / f"cat{cat_id}_depth{depth}_neo4j_times.csv"
        with open(neo4j_times_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["iteration", "execution_time_seconds"])
            for i, time_val in enumerate(result["neo4j"]["times"], 1):
                writer.writerow([i, time_val])

    def save_summary(self):
        """Save summary of all test results in JSON format."""
        tree_ancestry_summary_file = self.output_dir / "tree_ancestry_summary.json"
        with open(tree_ancestry_summary_file, "w") as f:
            json.dump(self.tree_ancestry_summary, f, indent=2)

        tree_all_summary_file = self.output_dir / "tree_all_summary.json"
        with open(tree_all_summary_file, "w") as f:
            json.dump(self.tree_all_summary, f, indent=2)

        breed_distribution_summary_file = self.output_dir / "breed_distribution_summary.json"
        with open(breed_distribution_summary_file, "w") as f:
            json.dump(self.breed_distribution_summary, f, indent=2)

        combined_summary = self._create_combined_summary()
        combined_summary_file = self.output_dir / "combined_summary.json"
        with open(combined_summary_file, "w") as f:
            json.dump(combined_summary, f, indent=2)

    def _create_combined_summary(self):
        """
        Create a combined summary comparing ancestry and all-info queries.

        Returns:
            list: List of dictionaries with comparative metrics
        """
        ancestry_by_depth = {entry["depth"]: entry for entry in self.tree_ancestry_summary}
        all_by_depth = {entry["depth"]: entry for entry in self.tree_all_summary}

        all_depths = sorted(set(list(ancestry_by_depth.keys()) + list(all_by_depth.keys())))

        combined = []
        for depth in all_depths:
            ancestry_entry = ancestry_by_depth.get(depth, {})
            all_entry = all_by_depth.get(depth, {})

            if not ancestry_entry or not all_entry:
                continue

            pg_ancestry_avg = ancestry_entry.get("postgres_avg", 0)
            pg_all_avg = all_entry.get("postgres_avg", 0)

            neo_ancestry_avg = ancestry_entry.get("neo4j_avg", 0)
            neo_all_avg = all_entry.get("neo4j_avg", 0)

            combined.append(
                {
                    "depth": depth,
                    "postgres_ancestry_avg": pg_ancestry_avg,
                    "postgres_all_avg": pg_all_avg,
                    "neo4j_ancestry_avg": neo_ancestry_avg,
                    "neo4j_all_avg": neo_all_avg,
                    "ancestry_winner": ancestry_entry.get("winner", "N/A"),
                    "all_winner": all_entry.get("winner", "N/A"),
                }
            )

        return sorted(combined, key=lambda x: x["depth"])
