import json
import os
import sys
from pathlib import Path

from termcolor import colored


def load_data_config() -> tuple:
    """
    Load configuration from data_config.json and return it.
    This function will find the config file regardless of where it's called from.

    :return: tuple containing absolute data paths and column types
    """
    script_path = Path(os.path.abspath(__file__))
    project_root = script_path.parents[2]

    config_path = project_root / "config" / "data_config.json"

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(colored(f"Error: Could not find data_config.json at {config_path}", "red"))
        sys.exit(1)

    data_path_initial = project_root / config["data_paths"]["initial"]
    data_path_helper = project_root / config["data_paths"]["helper"]
    data_path_processed = project_root / config["data_paths"]["processed"]
    data_path_final = project_root / config["data_paths"]["final"]

    data_paths = {
        "initial": data_path_initial,
        "helper": data_path_helper,
        "processed": data_path_processed,
        "final": data_path_final,
    }

    column_types = {}
    for key, value in config["column_types"].items():
        if value == "str":
            column_types[key] = str
        elif value == "int":
            column_types[key] = int
        elif value == "float":
            column_types[key] = float
        else:
            column_types[key] = value

    return data_paths, column_types


def load_config() -> dict:
    """
    Load configuration from config.json and return it.
    This function will find the config file regardless of where it's called from.

    :return: dictionary containing configuration settings
    """

    script_path = Path(os.path.abspath(__file__))
    project_root = script_path.parents[2]
    config_path = project_root / "config" / "config.json"

    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
            return config
    except FileNotFoundError:
        print(colored(f"Error: Could not find config.json at {config_path}", "red"))
        sys.exit(1)
    except Exception as e:
        print(colored(f"Error loading configuration: {e}", "red"))
        sys.exit(1)


def custom_print(message, level=1):
    """
    Custom print function to format messages with hierarchy and colors

    :param message: The message to print
    :param level: The hierarchy level of the message (1, 2). Default = 1
    """
    match level:
        case 1:
            print(colored("=" * 100, "blue"))
            print(colored(message, "magenta"))
            print(colored("=" * 100, "blue"))
        case 2:
            print(colored("~" * 50, "green"))
            print(colored(message, "yellow"))
            print(colored("~" * 50, "green"))
        case _:
            print("WRONG LEVEL")


def is_running_in_docker():
    """
    Detect if the application is running inside a Docker container

    Returns:
        bool: True if running in Docker, False otherwise
    """
    if os.environ.get("RUNNING_IN_DOCKER") == "true":
        return True

    return False
