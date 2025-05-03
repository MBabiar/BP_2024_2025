import glob
import logging
import sys
import time
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

NOTEBOOK_DIR = Path(__file__).parent


def get_notebooks():
    """Get all Phase notebooks sorted by number"""
    notebooks = glob.glob(str(NOTEBOOK_DIR / "Phase_*.ipynb"))
    notebooks.sort()  # Sort by phase number to ensure correct order of execution
    return notebooks


def execute_notebook(notebook_path):
    """Execute a notebook and save only the HTML output"""
    notebook_name = Path(notebook_path).stem

    logger.info(f"Processing {notebook_name}...")
    start_time = time.time()

    try:
        with open(notebook_path) as f:
            nb = nbformat.read(f, as_version=4)

        execute_processor = ExecutePreprocessor(timeout=1800)
        execute_processor.preprocess(nb, {"metadata": {"path": str(NOTEBOOK_DIR)}})

        elapsed_time = time.time() - start_time
        logger.info(f"Completed processing {notebook_name} in {elapsed_time:.2f} seconds")
        return True

    except Exception as e:
        logger.error(f"Error processing {notebook_name}: {str(e)}")
        return False


def main():
    """Main function to process all notebooks"""
    logger.info("Starting data processing...")

    notebooks = get_notebooks()
    logger.info(f"Found {len(notebooks)} notebooks to process")

    success_count = 0
    for notebook in notebooks:
        if execute_notebook(notebook):
            success_count += 1

    logger.info(f"Data processing complete! Successfully processed {success_count}/{len(notebooks)} notebooks")

    return 0 if success_count == len(notebooks) else 1


if __name__ == "__main__":
    sys.exit(main())
