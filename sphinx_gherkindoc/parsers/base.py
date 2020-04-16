"""Base classes for parsing."""


class BaseModel:
    """Base model for parsers."""

    def __init__(self, data):
        self._data = data

    def __getattr__(self, key):
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


class BaseFeature(BaseModel):
    """Feature base for parsers."""

    def __init__(self, root_path, source_path):
        self._data = None

    @property
    def examples(self):
        """Supports feature-level examples in some parsers."""
        return []
