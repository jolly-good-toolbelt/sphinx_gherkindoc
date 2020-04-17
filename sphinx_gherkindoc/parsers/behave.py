"""Helper functions for writing rST files with behave parser."""
import behave.parser

from .base import BaseFeature


class Feature(BaseFeature):
    """Feature model for Behave."""

    def __init__(self, root_path, source_path):
        self._data = behave.parser.parse_file(source_path)
