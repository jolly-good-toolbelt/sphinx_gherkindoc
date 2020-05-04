"""Helper functions for writing rST files with behave parser."""
from typing import List, Optional, Union

import behave.parser

from .base import BaseModel


class BehaveModel(BaseModel):
    """Custom model for Behave-parsed objects."""

    @property
    def description(self) -> Optional[List[str]]:
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

    def __init__(self, root_path: str, source_path: str):
        self._data = behave.parser.parse_file(source_path)

    @property
    def scenarios(self) -> List[Scenario]:
        """Wrap Behave Scenarios to include description processing."""
        return [Scenario(s) for s in self._data.scenarios]

    @property
    def examples(self) -> Union[behave.model.Examples, List]:
        """Supports dummy feature-level examples."""
        return []
