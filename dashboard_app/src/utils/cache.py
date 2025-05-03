from pathlib import Path

from flask_caching import Cache

from dashboard_app.src.utils.callback_utils import skip_cache_when_db_unhealthy
from dashboard_app.src.utils.logger import logger

_cache = None
CACHE_DIR = Path(__file__).parent.parent / "cache"


def init_cache(app) -> None:
    """
    Initialize the cache with the Flask app.

    Args:
        app: Flask application instance

    Returns:
        None
    """
    global _cache

    _cache = Cache(
        app.server,
        config={
            "CACHE_TYPE": "filesystem",
            "CACHE_DIR": CACHE_DIR,
            "CACHE_DEFAULT_TIMEOUT": 60 * 60 * 24,
            "CACHE_THRESHOLD": 1000,
        },
    )

    logger.debug(f"Cache initialized with directory: {CACHE_DIR}")


def get_cache() -> Cache:
    """
    Get the cache instance.

    Returns:
        Cache: Flask-Caching instance

    Raises:
        RuntimeError: If cache has not been initialized
    """
    global _cache
    if _cache is None:
        raise RuntimeError("Cache has not been initialized. Call init_cache(app) before using the cache.")

    return _cache


def clear_cache() -> None:
    """
    Clear all entries from the cache.

    Returns:
        None
    """
    global _cache
    if _cache is not None:
        _cache.clear()
        logger.debug("Cache cleared")
    else:
        logger.warning("⚠️ Cache not initialized, cannot clear")


class CacheManager:
    @staticmethod
    def get_cache():
        """Get the cache instance, returning None if not initialized yet"""
        global _cache
        return _cache

    @staticmethod
    def is_initialized():
        """Check if the cache is initialized"""
        global _cache
        return _cache is not None

    @staticmethod
    def memoize(timeout=None, args_to_ignore=None):
        """
        Custom memoization decorator for caching function results.

        Args:
            timeout: Time in seconds to store cache entries (default uses CACHE_DEFAULT_TIMEOUT)
            args_to_ignore: List of argument names to exclude from the cache key.
        """

        def decorator(func):
            def wrapper(*args, **kwargs):
                global _cache
                if _cache is not None:
                    return _cache.memoize(
                        timeout=timeout, unless=skip_cache_when_db_unhealthy, args_to_ignore=args_to_ignore
                    )(func)(*args, **kwargs)
                else:
                    logger.warning(f"Server cache not initialized, skipping cache for {func.__name__}")
                    return func(*args, **kwargs)

            return wrapper

        return decorator
