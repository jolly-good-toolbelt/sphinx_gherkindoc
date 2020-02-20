"""Sphinx-Gherkindoc Parsers."""
import importlib
from pathlib import Path


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
