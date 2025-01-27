import sys


class NoImport:
    """Simple context manager to prevent one or more named modules from being imported."""

    def __init__(self, *names: str) -> None:
        """
        :param names: The names of the modules to prevent from being imported.
        """
        self._names = names

    def __enter__(self) -> None:
        for name in self._names:
            # Set the module to None to prevent it from being imported.
            sys.modules[name] = None

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        for name in self._names:
            # Remove the module from sys.modules to clean up.
            del sys.modules[name]
