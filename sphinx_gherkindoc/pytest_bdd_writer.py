"""Helper functions for writing rST files."""
import importlib
import itertools
import pathlib
import re
import pkg_resources
from typing import List, Optional, Union

import pytest_bdd.feature

from .glossary import step_glossary
from .utils import INDENT_DEPTH, MAIN_STEP_KEYWORDS, QUOTE, rst_escape, SphinxWriter


PytestBddModel = Union[
    pytest_bdd.feature.Feature,
    pytest_bdd.feature.Background,
    pytest_bdd.feature.Scenario,
    pytest_bdd.feature.Step,
    pytest_bdd.feature.Examples,
]


# Simplified this from a class, for various reasons.
# Additional simplification work is needed!!!!
def feature_to_rst(
    source_path: pathlib.Path,
    root_path: pathlib.Path,
    url_from_tag: Optional[str] = "",
    integrate_background: bool = False,
    background_step_format: str = "{}",
) -> SphinxWriter:
    """Return a SphinxWriter containing the rST for the given feature file."""
    output_file = SphinxWriter()

    def _get_keyword(obj):
        keyword = getattr(obj, "keyword", obj.__class__.__name__.rsplit(".", 1)[-1])
        if keyword == "Scenario" and obj.examples.examples:
            return "Scenario Outline"
        return keyword

    def section(level: int, obj: PytestBddModel) -> None:
        keyword = _get_keyword(obj)
        name = getattr(obj, "name", "") or ""
        section_name = f"{keyword}: {rst_escape(name)}"
        output_file.create_section(level, section_name.rstrip(": "))

    def description(description: Union[str, List[str]]) -> None:
        if not description:
            return
        if not isinstance(description, list):
            description = [description]
        for line in description:
            output_file.add_output(rst_escape(line), indent_by=INDENT_DEPTH)
            # Since behave strips newlines, a reasonable guess must be made as
            # to when a newline should be re-inserted
            if line[-1] == "." or line == description[-1]:
                output_file.blank_line()

    def text(text: Union[str, List[str]]) -> None:
        if not text:
            return
        if not isinstance(text, list):
            text = [text]
        output_file.blank_line()
        output_file.add_output("::", line_breaks=2)
        # Since text blocks are treated as raw text, any new lines in the
        # Gherkin are preserved. To convert the text block into a code block,
        # each new line must be indented.
        for line in itertools.chain(*(x.splitlines() for x in text)):
            output_file.add_output(
                rst_escape(line), line_breaks=2, indent_by=INDENT_DEPTH
            )

    # Build the URL parser once since `ticket_url_or_tag` is called multiple times
    url_parser = lambda x: ""  # noqa: E731
    for entry_point in pkg_resources.iter_entry_points("parsers"):
        if entry_point.name == "url":
            url_parser = entry_point.load()
    if url_from_tag:
        url_module, url_function = url_from_tag.split(":", maxsplit=1)
        parser_module = importlib.import_module(url_module)
        url_parser = getattr(parser_module, url_function)

    # Reference link here because it's too long to put inside the function itself.
    # http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#embedded-uris-and-aliases
    def ticket_url_or_tag(tag: str) -> str:
        """Get a URL or tag.

        If tag is a ticket, return an anonymous embedded hyperlink for it,
        else tag itself.
        """
        url = url_parser(tag)
        if url:
            return f"`{tag} <{url}>`__"
        return tag

    def tags(tags: List[str], *parent_objs: PytestBddModel) -> None:
        parent_with_tags = tuple(x for x in parent_objs if x.tags)
        if not (tags or parent_with_tags):
            return
        output_file.add_output(".. pull-quote::", line_breaks=2)
        tag_str = ", ".join(map(ticket_url_or_tag, tags))
        for obj in parent_with_tags:
            tags_list = ", ".join(map(ticket_url_or_tag, obj.tags))
            tag_str += f" (Inherited from {_get_keyword(obj)}: {tags_list} )"
        output_file.add_output(
            f"Tagged: {tag_str.strip()}", line_breaks=2, indent_by=INDENT_DEPTH
        )

    def format_step(step: pytest_bdd.feature.Step, step_format: str) -> str:
        # Make bold any scenario outline variables
        formatted_step = re.sub(r"(\\\<.*?\>)", r"**\1**", rst_escape(step.name))
        # Apply the step format string
        formatted_step = step_format.format(f"{step.keyword} {formatted_step}")
        return formatted_step

    def _step_table(step):
        return getattr(step, "table", "")

    def _step_text(step):
        return getattr(step, "text", getattr(step, "lines", ""))

    def _step_filename(step):
        return getattr(
            step, "filename", (step.scenario or step.background).feature.filename
        )

    def _step_line(step):
        return getattr(step, "line", step.line_number)

    def steps(steps: List[pytest_bdd.feature.Step], step_format: str = "{}") -> None:
        any_step_has_table_or_text = any(
            _step_table(step) or _step_text(step) for step in steps
        )
        for step in steps:
            step_glossary[step.name.lower()].add_reference(
                step.name,
                pathlib.Path(_step_filename(step)).resolve().relative_to(root_path),
                _step_line(step),
            )
            formatted_step = format_step(step, step_format)
            # Removing the dash, but still having the pipe character
            # makes the step slightly indented, and without a dash.
            # This creates a nice visual of "sections" of steps.
            # However, this creates odd results when there is a step text or step table
            # anywhere in the scenario.
            # In that case, we stick to a simple bullet list for all steps.
            prefix = (
                "| -"
                if (any_step_has_table_or_text or step.keyword in MAIN_STEP_KEYWORDS)
                else "| "
            )
            output_file.add_output(f"{prefix} {formatted_step}")
            if _step_table(step):
                output_file.blank_line()
                table(_step_table(step), inline=True)
                output_file.blank_line()
            if _step_text(step):
                text(_step_text(step))

    def examples(
        scenario: Optional[pytest_bdd.feature.Scenario],
        feature: pytest_bdd.feature.Feature,
    ) -> None:
        if scenario:
            obj = scenario
            tag_objects = [scenario, feature]
        else:
            obj = feature
            tag_objects = []
        example_obj = getattr(obj, "examples", [])
        if not example_obj.examples:
            return
        section(3, example_obj)
        tags(obj.tags, *tag_objects)
        table(example_obj)
        output_file.blank_line()

    def table(table: pytest_bdd.feature.Examples, inline: bool = False) -> None:
        indent_by = INDENT_DEPTH if inline else 0
        directive = ".. csv-table::"
        output_file.add_output(directive, indent_by=indent_by)
        headers = '", "'.join(table.example_params)
        indent_by += INDENT_DEPTH
        output_file.add_output(f':header: "{headers}"', indent_by=indent_by)
        output_file.add_output(f":quote: {QUOTE}", line_breaks=2, indent_by=indent_by)
        for row in table.examples:
            row = f"{QUOTE}, {QUOTE}".join(map(rst_escape, row))
            output_file.add_output(f"{QUOTE}{row}{QUOTE}", indent_by=indent_by)

    feature = pytest_bdd.feature.Feature(
        root_path, pathlib.Path(source_path).resolve().relative_to(root_path)
    )
    section(1, feature)
    description(feature.description)
    if feature.examples.examples:
        examples(None, feature)
    if feature.background and not integrate_background:
        section(2, feature.background)
        steps(feature.background.steps)
        output_file.blank_line()
    for scenario in feature.scenarios.values():
        section(2, scenario)
        tags(scenario.tags, feature)
        description(scenario.description)
        if integrate_background and feature.background:
            steps(feature.background.steps, step_format=background_step_format)
        steps(scenario.steps)
        output_file.blank_line()
        examples(scenario, feature)

    return output_file
