"""Helper functions for writing rST files."""
from collections import namedtuple
from typing import List, Optional, Union
import pathlib

import pytest_bdd.feature

from .base import BaseModel

BlankString = str
InlineTable = namedtuple("InlineTable", ["headings", "rows"])


class PytestModel(BaseModel):
    """Base Model for Pytest-Bdd objects."""

    @property
    def description(self) -> Optional[List[str]]:
        """Return description as a list of lines."""
        description = getattr(self._data, "description", None)
        if description:
            lines = list(description.split("\n"))
            lines.append("")
            return lines
        return description

    @property
    def keyword(self) -> str:
        """Return the keyword for a given item."""
        keyword = getattr(
            self._data, "keyword", self._data.__class__.__name__.rsplit(".", 1)[-1]
        )
        if keyword == "Scenario" and self._data.examples.examples:
            return "Scenario Outline"
        return keyword

    @property
    def name(self) -> str:
        """Return the name for a given item, if available."""
        return getattr(self._data, "name", None) or ""


class Step(PytestModel):
    """Step model for Pytest-Bdd."""

    @property
    def filename(self) -> str:
        """Return the source file path for the step."""
        parent = self._data.scenario or self._data.background
        return parent.feature.filename

    @property
    def line(self) -> int:
        """Return the line number from the source file."""
        return self._data.line_number

    @property
    def step_type(self) -> str:
        """Return the step type/keyword."""
        return self.keyword

    @property
    def table(self) -> Union[InlineTable, BlankString]:
        """Return the step table, if present."""
        lines = self._data.lines
        if lines and all("|" in x for x in lines):
            rows = [l.strip().split("|") for l in lines]
            rows = [
                list(filter(None, (entry.strip() for entry in row))) for row in rows
            ]
            return InlineTable(headings=rows[0], rows=rows[1:])
        return ""

    @property
    def text(self) -> Union[List[str], BlankString]:
        """Return the (non-table) multi-line text from a step."""
        if self.table:
            # pytest-bdd doesn't distinguish between table and text
            # in the same way as behave,
            # so we determine whether the lines are a table,
            # and return only non-table lines.
            return ""
        return [
            l.strip() for l in self._data.lines if not set(l).issubset({"'", '"', " "})
        ]

    @property
    def name(self) -> str:
        """Return text after keyword."""
        return self._data.name.splitlines()[0]


class Background(PytestModel):
    """Background model for Pytest-Bdd."""

    @property
    def steps(self) -> List[Step]:
        """Return the steps from the background."""
        return [Step(s) for s in self._data.steps]


class Example(PytestModel):
    """Example model for Pytest-Bdd."""

    @property
    def tags(self) -> list:
        """Return an empty list of tags, as Pytest-Bdd does not support example tags."""
        return []

    @property
    def table(self) -> InlineTable:
        """Return the Example table."""
        return InlineTable(headings=self._data.example_params, rows=self._data.examples)


class Scenario(PytestModel):
    """Scenario model for Pytest-Bdd."""

    @property
    def steps(self) -> List[Step]:
        """Return (non-background) steps for the scenario."""
        return [Step(s) for s in self._data.steps if not s.background]

    @property
    def examples(self) -> List[Optional[Example]]:
        """Return examples from the scenario, if any exist."""
        if self._data.examples.examples:
            return [Example(self._data.examples)]
        return []


class Feature(PytestModel):
    """Feature model for Pytest-Bdd."""

    def __init__(self, root_path: str, source_path: str):
        self._data = pytest_bdd.feature.Feature(
            root_path, pathlib.Path(source_path).resolve().relative_to(root_path)
        )

    @property
    def scenarios(self) -> List[Scenario]:
        """Return all scenarios for the feature."""
        return [Scenario(s) for s in self._data.scenarios.values()]

    @property
    def background(self) -> Optional[Background]:
        """Return the background for the feature."""
        background_entry = self._data.background
        return Background(background_entry) if background_entry else None

    @property
    def examples(self) -> List[Optional[Example]]:
        """Return feature-level examples, if any exist."""
        if self._data.examples.examples:
            return [Example(self._data.examples)]
        return []
