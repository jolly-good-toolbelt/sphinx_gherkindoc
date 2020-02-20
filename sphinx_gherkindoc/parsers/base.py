"""Base classes for parsing."""


class BaseModel:
    """Base model for parsers."""

    def __init__(self, data):
        self._data = data

    def __getattr__(self, key):
        """Grab attribute from wrapped class, if present."""
        return getattr(self._data, key)


class BaseFeature(BaseModel):
    """Feature base for parsers."""

    def __init__(self, root_path, source_path):
        self._data = None

    @property
    def examples(self):
        """Supports feature-level examples in some parsers."""
        return []
