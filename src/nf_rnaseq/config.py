import os

REQUESTS_CACHE_VAR = "REQUESTS_CACHE"
"""str: Environment variable for requests cache file prefix."""


def set_requests_cache(val: str) -> None:
    """Set the requests cache path in environment variables.

    Parameters
    ----------
    val : str
        Requests cache path

    Returns
    -------
    None

    """
    os.environ[REQUESTS_CACHE_VAR] = val


def maybe_get_requests_cache() -> str | None:
    """Get the requests cache path from the environment.

    Returns
    -------
    str | None
        Requests cache path as string if exists, otherwise None

    """
    try:
        return os.environ[REQUESTS_CACHE_VAR]
    except KeyError:
        return None
