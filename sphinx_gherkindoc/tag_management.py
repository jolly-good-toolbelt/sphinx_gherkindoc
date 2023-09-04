"""Module specific functions for tag management and document building."""
from .utils import SphinxWriter
from typing import Set, Optional
from functools import reduce


tag_set: Set[str] = set()


def make_tag_list(project_name: str) -> Optional[SphinxWriter]:
    """Make caller to finalize a tag list."""
    if not tag_set:
        return None
    tag_list_sphinx_doc = SphinxWriter()
    tag_list_sphinx_doc = tag_list_preamble(tag_list_sphinx_doc, project_name)
    tag_list_sphinx_doc = reduce(
        lambda acc, t: add_tag(acc, t), sorted(tag_set), tag_list_sphinx_doc
    )
    return tag_list_sphinx_doc


def tag_list_preamble(sphinx_dox: SphinxWriter, project_name: str) -> SphinxWriter:
    """Add a preamble to the tag list."""
    sphinx_dox.create_section(1, f"{project_name} Tag List")
    return sphinx_dox


def add_tag(sphinx_dox: SphinxWriter, tag: str) -> SphinxWriter:
    """Map function over tag list."""
    sphinx_dox.add_output(f"* {tag}")
    sphinx_dox.blank_line()
    return sphinx_dox
