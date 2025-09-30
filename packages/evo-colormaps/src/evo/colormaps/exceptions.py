from evo.common.exceptions import EvoClientException


class UnknownColormapResponse(EvoClientException):
    """Raised when an unknown colormap response is returned from the server."""


class UnknownColormapType(EvoClientException):
    """Raised when attempting to upload a colormap type that is unknown."""
