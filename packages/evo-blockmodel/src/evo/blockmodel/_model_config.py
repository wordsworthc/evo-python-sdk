from pydantic import BaseModel, ConfigDict


class CustomBaseModel(BaseModel):
    """Custom base model for providing a global configuration to generated models."""

    model_config = ConfigDict(
        extra="allow",
        protected_namespaces=(),
    )
