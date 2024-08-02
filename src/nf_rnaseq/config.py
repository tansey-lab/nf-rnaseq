import os

REQUESTS_CACHE_VAR = "REQUESTS_CACHE"
"""str: Environment variable for request cache file prefix."""


def set_request_cache(val: str) -> None:
    """Set the request cache path in environment variables.

    Parameters
    ----------
    val : str
        Request cache path

    Returns
    -------
    None

    """
    os.environ[REQUESTS_CACHE_VAR] = val


def maybe_get_request_cache() -> str | None:
    """Get the request cache path from the environment.

    Returns
    -------
    str | None
        Request cache path as string if exists, otherwise None

    """
    try:
        return os.environ[REQUESTS_CACHE_VAR]
    except KeyError:
        return None
