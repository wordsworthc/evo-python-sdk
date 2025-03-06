from evo.common.exceptions import EvoClientException

__all__ = ["UserPermissionTypeError"]


class UserPermissionTypeError(TypeError, EvoClientException):
    """The requested user permission has the wrong type"""
