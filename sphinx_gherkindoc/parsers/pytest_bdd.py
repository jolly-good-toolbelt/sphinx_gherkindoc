"""Helper functions for writing rST files."""
from collections import namedtuple
import pathlib

import pytest_bdd.feature

from .base import BaseModel

InlineTable = namedtuple("InlineTable", ["headings", "rows"])


class PytestModel(BaseModel):
    """Base Model for Pytest-Bdd objects."""

    @property
    def keyword(self):
        """Return the keyword for a given item."""
        keyword = getattr(
            self._data, "keyword", self._data.__class__.__name__.rsplit(".", 1)[-1]
        )
        if keyword == "Scenario" and self._data.examples.examples:
            return "Scenario Outline"
        return keyword

    @property
    def name(self):
        """Return the name for a given item, if available."""
        return getattr(self._data, "name", None) or ""


class Step(PytestModel):
    """Step model for Pytest-Bdd."""

    @property
    def filename(self):
        """Return the source file path for the step."""
        parent = self._data.scenario or self._data.background
        return parent.feature.filename

    @property
    def line(self):
        """Return the line number from the source file."""
        return self._data.line_number

    @property
    def step_type(self):
        """Return the step type/keyword."""
        return self.keyword

    @property
    def table(self):
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
    def text(self):
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
    def name(self):
        """Return text after keyword."""
        return self._data.name.splitlines()[0]


class Background(PytestModel):
    """Background model for Pytest-Bdd."""

    @property
    def steps(self):
        """Return the steps from the background."""
        return [Step(s) for s in self._data.steps]


class Example(PytestModel):
    """Example model for Pytest-Bdd."""

    @property
    def tags(self):
        """Return an empty list of tags, as Pytest-Bdd does not support example tags."""
        return []

    @property
    def table(self):
        """Return the Example table."""
        return InlineTable(headings=self._data.example_params, rows=self._data.examples)


class Scenario(PytestModel):
    """Scenario model for Pytest-Bdd."""

    @property
    def steps(self):
        """Return (non-background) steps for the scenario."""
        return [Step(s) for s in self._data.steps if not s.background]

    @property
    def examples(self):
        """Return examples from the scenario, if any exist."""
        if self._data.examples.examples:
            return [Example(self._data.examples)]
        return []


class Feature(PytestModel):
    """Feature model for Pytest-Bdd."""

    def __init__(self, root_path, source_path):
        self._data = pytest_bdd.feature.Feature(
            root_path, pathlib.Path(source_path).resolve().relative_to(root_path)
        )

    @property
    def scenarios(self):
        """Return all scenarios for the feature."""
        return [Scenario(s) for s in self._data.scenarios.values()]

    @property
    def background(self):
        """Return the background for the feature."""
        return Background(self._data.background)

    @property
    def examples(self):
        """Return feature-level examples, if any exist."""
        if self._data.examples.examples:
            return [Example(self._data.examples)]
        return []
