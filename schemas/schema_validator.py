from jsonschema import validate, ValidationError
import json


class SchemaValidationError(Exception):
    """Raised when output does not conform to schema."""


def validate_against_schema(data: dict, schema: dict):
    """
    Hard schema validation.
    Raises SchemaValidationError if invalid.
    """
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise SchemaValidationError(
            f"Schema validation failed: {e.message}"
        ) from e
