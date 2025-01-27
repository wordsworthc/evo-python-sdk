"""Utilities for interacting with pydantic v1 OR v2"""

import warnings
from collections.abc import Mapping
from typing import Any, TypeVar

from pydantic import BaseModel, Field
from pydantic.version import VERSION as PYDANTIC_VERSION

# Deprecation warning that this module is deprecated and will be arbitrarily removed at a later date.
# The ultimate removal of this module should not be considered a breaking change.
warnings.warn(
    "The module evo.common.pydantic_utils is deprecated and may be arbitrarily removed in any future release.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "export_dict",
    "export_json",
    "validate_model",
    "validator",
    "BaseModel",
    "Field",
    "FrozenBaseModel",
    "PYDANTIC_V2",
    "T_BaseModel",
]

T_BaseModel = TypeVar("T_BaseModel", bound=BaseModel)

PYDANTIC_V2 = PYDANTIC_VERSION.startswith("2.")

if not PYDANTIC_V2:
    # Pydantic v1 implementation.
    from pydantic import validator

    class FrozenBaseModel(BaseModel):
        class Config:
            allow_mutation = False

        def __hash__(self) -> int:
            return hash((self.__class__,) + tuple(self.__fields__.values()))

    def export_dict(model: BaseModel) -> dict[str, Any]:
        """Convert a pydantic model to a serializable python dictionary.

        :param model: The model instance for serialization.

        :return: The serialized model.
        """
        return model.dict(by_alias=True)

    def export_json(model: BaseModel) -> str:
        """Convert a pydantic model to json.

        :param model: The model instance for serialization.

        :return: The serialized model.
        """
        return model.json(by_alias=True)

    def validate_model(data: Mapping[str, Any], klass: type[T_BaseModel]) -> T_BaseModel:
        """Deserializes list or dict to an API model.

        :param data: model dict.
        :param klass: API model class literal.

        :return: API model object.
        """
        return klass.parse_obj(data)

else:
    # Pydantic v2 implementation.
    from pydantic import field_validator as validator

    class FrozenBaseModel(BaseModel, frozen=True):
        def __hash__(self) -> int:
            return hash((self.__class__,) + tuple(self.model_fields.values()))

    def export_dict(model: BaseModel) -> dict[str, Any]:
        """Convert a pydantic model to a serializable python dictionary.

        :param model: The model instance for serialization.

        :return: The serialized model.
        """
        return model.model_dump(mode="json", by_alias=True)

    def export_json(model: BaseModel) -> str:
        """Convert a pydantic model to json.

        :param model: The model instance for serialization.

        :return: The serialized model.
        """
        return model.model_dump_json(by_alias=True)

    def validate_model(data: Mapping[str, Any], klass: type[T_BaseModel]) -> T_BaseModel:
        """Deserializes list or dict to an API model.

        :param data: model dict.
        :param klass: API model class literal.

        :return: API model object.
        """
        return klass.model_validate(data)
