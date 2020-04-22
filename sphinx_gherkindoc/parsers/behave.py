"""Helper functions for writing rST files with behave parser."""
import behave.parser

from .base import BaseModel


class BehaveModel(BaseModel):
    @property
    def description(self):
        """Add some reasonable assumptions about line breaks into descriptions.

        Any line that ends in a period will have a newline added for separation.

        Additionally, a newline will be added after the final line.
        """
        raw_description_lines = self._data.description
        processed_description_lines = []
        for idx, line in enumerate(raw_description_lines, start=1):
            processed_description_lines.append(line)
            if line.endswith(".") or idx == len(raw_description_lines):
                processed_description_lines.append("")
        return processed_description_lines


class Scenario(BehaveModel):
    """Make Scenarios inherit the ``BehaveModel`` description property."""
    pass


class Feature(BehaveModel):
    """Feature model for Behave."""

    def __init__(self, root_path, source_path):
        self._data = behave.parser.parse_file(source_path)

    @property
    def scenarios(self):
        """Wrap Behave Scenarios to include description processing."""
        return [Scenario(s) for s in self._data.scenarios]

    @property
    def examples(self):
        """Supports dummy feature-level examples."""
        return []
