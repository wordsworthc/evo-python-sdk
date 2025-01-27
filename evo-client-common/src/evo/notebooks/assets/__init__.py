from importlib.abc import Traversable
from importlib.resources import files

_ROOT = files(__name__)


def get(filename: str) -> Traversable:
    """Get the path to a file in this directory.

    :param filename: The name of the file.

    :return: A Traversable object representing the file.
    """
    return _ROOT / filename
