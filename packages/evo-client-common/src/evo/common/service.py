from .connector import ApiConnector
from .data import Environment

__all__ = ["BaseServiceClient"]


class BaseServiceClient:
    """Base class that may be used for individual service clients.

    Defines including cache management and environment variables.
    """

    def __init__(self, environment: Environment, connector: ApiConnector) -> None:
        """
        :param environment: The environment object
        :param connector: The connector object.
        """
        self._environment = environment
        self._connector = connector
