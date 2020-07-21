"""Sphinx-Gherkindoc Parsers."""
import importlib
from pathlib import Path
from typing import List, Union

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore


parsers = {}

for file in Path(__file__).parent.glob("*.py"):
    name = file.stem
    if name.startswith("_"):
        continue
    try:
        module = importlib.import_module(f"sphinx_gherkindoc.parsers.{name}")
    except ImportError:
        continue
    feature = getattr(module, "Feature", None)
    if not feature:
        continue
    parsers[name] = feature


class ExamplesTableClass(Protocol):
    """Protocol for an examples table class model."""

    tags: List[str]


class StepClass(Protocol):
    """Protocol for a step class model."""

    name: str
    keyword: str


class ScenarioClass(Protocol):
    """Protocol for a scenario class model."""

    examples: List[ExamplesTableClass]
    tags: List[str]
    steps: List[StepClass]


class FeatureClass(Protocol):
    """Protocol for a feature class model."""

    scenarios: List[ScenarioClass]
    examples: List[ExamplesTableClass]
    tags: List[str]


ClassWithExamples = Union[FeatureClass, ScenarioClass]
