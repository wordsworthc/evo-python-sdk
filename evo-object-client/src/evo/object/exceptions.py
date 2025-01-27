from uuid import UUID

from evo.common.exceptions import CustomRFC87Error, EvoClientException


class SchemaIDFormatError(EvoClientException):
    """Unrecognized schema id format."""


class ObjectUUIDError(EvoClientException):
    """Object UUID is an unexpected value."""


class UnknownSchemaError(EvoClientException):
    """Unknown object schema."""

    def __init__(self, schema_id: str | None, detail: str):
        self.schema_id = schema_id
        self.detail = detail

    def __str__(self) -> str:
        return f"Could not resolve schema with id: '{self.schema_id}'\ndetail: {self.detail}"


class TableFormatError(EvoClientException):
    """The table structure does not match the expected Geoscience Object Schema data structure"""


class SchemaValidationError(EvoClientException):
    """Failed to validate data against a geoscience object schema"""


class ObjectAlreadyExistsError(CustomRFC87Error):
    TYPE_ID = "/geoscienceobject/objects/already-exists"

    @property
    def existing_id(self) -> UUID | None:
        if "existing_id" in self.content:
            return UUID(self.content["existing_id"])
        else:
            return None

    @property
    def object_path(self) -> str | None:
        if "object_path" in self.content:
            return str(self.content["object_path"])
        else:
            return None

    def __str__(self) -> str:
        error_message = super().__str__()
        if object_path := self.object_path:
            error_message += f"\nPath: {object_path}"
        if existing_id := self.existing_id:
            error_message += f"\nExisting ID: {existing_id}"
        return error_message
