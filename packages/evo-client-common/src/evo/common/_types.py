import os
from pathlib import Path
from typing import TypeAlias

from evo import logging

from .exceptions import FileNameTooLongError

__all__ = [
    "PathLike",
    "resolve_path",
]

logger = logging.getLogger("types")

PathLike: TypeAlias = str | os.PathLike | Path


MAX_WINDOWS_PATH_LEN = 259
FILE_NAME_TOO_LONG_ERR_NO = 63


def _check_path_length(path: Path) -> None:
    if os.name == "posix":
        try:
            max_path_length = os.pathconf(path, "PC_PATH_MAX")  # https://linux.die.net/man/3/pathconf
        except OSError as e:
            if e.errno == FILE_NAME_TOO_LONG_ERR_NO:
                raise FileNameTooLongError()
            else:
                logger.error("Error checking path length. Assuming path is not too long.", exc_info=True)
                return
        except ValueError:
            logger.error("Error checking path length. Assuming path is not too long.", exc_info=True)
            return
    elif os.name == "nt":
        max_path_length = MAX_WINDOWS_PATH_LEN
    else:
        logger.error("Unsupported operating system. Assuming path is not too long.")
        return

    if len(str(path)) > max_path_length:
        raise FileNameTooLongError()


def resolve_path(path: PathLike, *, check_path_length: bool = False) -> Path:
    """Resolve the given path and check for maximum path length.

    :param path: The path to resolve.
    :param check_path_length: If True, check the path length.

    :returns: The resolved path.

    :raises TypeError: If the path is not a PathLike object.
    :raises FileNameTooLongError: If check_path_length is True and the path is too long.
    """
    if not isinstance(path, Path):
        try:
            path = Path(path)
        except TypeError:
            raise TypeError(f"Expected a PathLike object, got {path!r}")

    resolved = path.resolve()
    if check_path_length:
        _check_path_length(resolved)
    return resolved
