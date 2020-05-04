"""Base classes for parsing."""
from typing import Any


class BaseModel:
    """Base model for parsers."""

    def __init__(self, data: Any):
        self._data = data

    def __getattr__(self, key: str) -> Any:
        """Grab attribute from wrapped class, if present.

        When inheriting this model,
        properties may need to be added to the subclass
        in cases where a specific ``behave`` attribute
        does not exist on the underlying class,
        or where the format returned from the underlying attribute
        does not match the ``behave`` format.
        """
        if key == "description":
            # Workaround for current pytest-bdd release (3.2.1),
            # which does not have a scenario.description attribute.
            return getattr(self._data, key, None)
        return getattr(self._data, key)
