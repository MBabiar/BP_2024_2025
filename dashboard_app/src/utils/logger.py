"""
Utility module for logging and messages throughout the application.
Provides a centralized way to control verbosity of log messages.
"""

import sys
from datetime import datetime

from termcolor import colored


class Logger:
    """
    A simple logger class that supports global verbosity control.
    """

    _instance = None
    _verbose = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    @classmethod
    def set_verbose(cls, verbose: bool) -> None:
        """
        Set global verbosity level.

        Args:
            verbose (bool): True for verbose output, False otherwise
        """
        cls._verbose = verbose

    @classmethod
    def is_verbose(cls) -> bool:
        """
        Check if verbose mode is enabled.

        Returns:
            bool: True if verbose mode is on, False otherwise
        """
        return cls._verbose

    @classmethod
    def debug(cls, message: str) -> None:
        """
        Log debug message only if verbose mode is on.

        Args:
            message (str): Message to log
        """
        if cls._verbose:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(colored(f"[DEBUG] {timestamp} - {message}", "blue"), file=sys.stderr)

    @classmethod
    def info(cls, message: str) -> None:
        """
        Log informational message (always shown).

        Args:
            message (str): Message to log
        """
        if cls._verbose:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[INFO] {timestamp} - {message}", file=sys.stderr)

    @classmethod
    def warning(cls, message: str) -> None:
        """
        Log warning message (always shown).

        Args:
            message (str): Message to log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(colored(f"[WARNING] {timestamp} - {message}", "yellow"), file=sys.stderr)

    @classmethod
    def error(cls, message: str) -> None:
        """
        Log error message (always shown).

        Args:
            message (str): Message to log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(colored(f"[ERROR] {timestamp} - {message}", "red"), file=sys.stderr)


logger = Logger()
