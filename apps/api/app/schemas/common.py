"""Shared pydantic types used across response schemas."""

from typing import Annotated

from pydantic import BeforeValidator

# UUID columns come back as uuid.UUID objects from the ORM; serializers want a
# plain string. This annotated type accepts both and always emits a string.
UuidStr = Annotated[str, BeforeValidator(lambda v: str(v) if v is not None else v)]
