import re

import dotenv

from evo import logging
from evo.common import ICache

__all__ = ["DotEnv"]

logger = logging.getLogger(__name__)

_KEY = re.compile(r"^[A-Z0-9_\-\.]+$", flags=re.IGNORECASE)


class DotEnv:
    """A simple wrapper around `python-dotenv` to manage and cache environment variables."""

    def __init__(self, cache: ICache, filename: str = ".env") -> None:
        self._file = cache.root / filename
        self._file.touch(exist_ok=True)
        self._cache = dotenv.dotenv_values(self._file, encoding="utf-8")

    def get(self, key: str, default: str | None = None) -> str | None:
        logger.debug(f"Getting environment variable: {key}")
        return self._cache.get(key, default)

    def set(self, key: str, value: str | None) -> None:
        logger.debug(f"Updating environment variable: {key}={value!r}")
        if not _KEY.match(key):
            raise ValueError(f"Invalid key: {key!r}")
        elif value is not None and not isinstance(value, str):
            raise ValueError(f"Invalid value for key {key}: {value!r}")
        elif value is None:
            dotenv.unset_key(self._file, key)
            self._cache.pop(key, None)
        else:
            dotenv.set_key(self._file, key, value, quote_mode="always", encoding="utf-8")
            self._cache[key] = value
