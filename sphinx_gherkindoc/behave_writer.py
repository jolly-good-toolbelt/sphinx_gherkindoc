"""Helper functions for writing rST files with behave parser."""
import importlib
import itertools
import pathlib
import re
from typing import Callable, List, Optional, Union

import behave.parser
import behave.model
import behave.model_core

from .glossary import step_glossary
from .utils import (
    AVAILABLE_ROLES,
    INDENT_DEPTH,
    QUOTE,
    rst_escape,
    SphinxWriter,
    role_name_from,
    apply_role,
)

BehaveModelWithDescription = Union[
    behave.model.Feature, behave.model.Scenario, behave.model.ScenarioOutline
]


# Simplified this from a class, for various reasons.
# Additional simplification work is needed!!!!
def feature_to_rst(
    source_path: pathlib.Path,
    root_path: pathlib.Path,
    url_parser: Optional[Callable] = None,
    url_from_tag: Optional[str] = "",
    integrate_background: bool = False,
    background_step_format: str = "{}",
) -> SphinxWriter:
    """Return a SphinxWriter containing the rST for the given feature file."""
    output_file = SphinxWriter()

    def section(level: int, obj: behave.model_core.BasicStatement) -> None:
        keyword = obj.keyword
        # "scenario outline" causes issues in the role name,
        # so we format the role name before applying it.
        keyword_role = role_name_from(f"gherkin-{keyword}-keyword")
        content_role = role_name_from(f"gherkin-{keyword}-content")
        content = rst_escape(obj.name)
        section_name = " ".join(
            [
                apply_role(keyword_role, f"{keyword}:"),
                apply_role(content_role, content) if content else "",
            ]
        )
        output_file.create_section(level, section_name.rstrip(": "))

    def description(obj: BehaveModelWithDescription) -> None:
        description = obj.description
        if not description:
            return
        if not isinstance(description, list):
            description = [description]

        # The keyword here will be capitalized and may contain a space,
        # so we sanitize it first.
        role = role_name_from(f"gherkin-{obj.keyword}-description")
        if role == "gherkin-scenario-outline-description":
            # Scenario and Scenario Outline description roles are considered the same
            role = "gherkin-scenario-description"

        for line in description:
            output_file.add_output(
                apply_role(role, rst_escape(line)), indent_by=INDENT_DEPTH
            )
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
        url = url_parser(tag) if url_parser else ""
        if url:
            return f"`{tag} <{url}>`__"
        return tag

    def tags(tags: List[str], *parent_objs: behave.model_core.BasicStatement) -> None:
        parent_with_tags = tuple(x for x in parent_objs if x.tags)
        if not (tags or parent_with_tags):
            return
        output_file.add_output(".. pull-quote::", line_breaks=2)
        tag_str = ", ".join(map(ticket_url_or_tag, tags))
        for obj in parent_with_tags:
            tags_list = ", ".join(map(ticket_url_or_tag, obj.tags))
            tag_str += f" (Inherited from {obj.keyword}: {tags_list} )"
        output_file.add_output(
            " ".join(
                [
                    apply_role("gherkin-tag-keyword", "Tagged:"),
                    # Because nested inline markup is not possible,
                    # we much choose between allowing tags to have links,
                    # or allowing them to be formatted.
                    # It is concluded that tag links are much more useful.
                    # See https://docutils.sourceforge.io/FAQ.html#is-nested-inline-markup-possible.  # noqa
                    # If rST supports this, we can add the following line:
                    #     apply_role("gherkin-tag-content", <content-on-line-below>),
                    tag_str.strip(),
                ]
            ),
            line_breaks=2,
            indent_by=INDENT_DEPTH,
        )

    def format_step(step: behave.model.Step, step_format: str) -> str:
        # Make bold any scenario outline variables
        formatted_step = re.sub(r"(\\\<.*?\>)", r"**\1**", rst_escape(step.name))
        formatted_step = step_format.format(
            " ".join(
                [
                    apply_role("gherkin-step-keyword", step.keyword),
                    # Because nested inline markup is not possible,
                    # we much choose between making params bold,
                    # or allowing step content to be formatted.
                    # Making params bold is the current behavior
                    # at the time of this implementation, so that is the current choice.
                    # See https://docutils.sourceforge.io/FAQ.html#is-nested-inline-markup-possible.  # noqa
                    # If rST supports this, we can add the following line:
                    #     apply_role("gherkin-step-content", <content-on-line-below>),
                    formatted_step,
                ]
            )
        )
        return formatted_step

    def steps(steps: List[behave.model.Step], step_format: str = "{}") -> None:
        for step in steps:
            step_glossary[step.name.lower()].add_reference(
                step.name,
                pathlib.Path(step.filename).resolve().relative_to(root_path),
                step.line,
            )
            formatted_step = format_step(step, step_format)
            output_file.add_output(f"| {formatted_step}")
            if step.table:
                output_file.blank_line()
                table(step.table, inline=True)
                output_file.blank_line()
            if step.text:
                text(step.text)

    def examples(
        scenario: behave.model.Scenario, feature: behave.model.Feature
    ) -> None:
        for example in getattr(scenario, "examples", []):
            section(3, example)
            tags(example.tags, scenario, feature)
            table(example.table)
            output_file.blank_line()

    def table(table: behave.model.Table, inline: bool = False) -> None:
        indent_by = INDENT_DEPTH if inline else 0
        directive = ".. csv-table::"
        output_file.add_output(directive, indent_by=indent_by)
        headers = '", "'.join(table.headings)
        indent_by += INDENT_DEPTH
        output_file.add_output(f':header: "{headers}"', indent_by=indent_by)
        output_file.add_output(f":quote: {QUOTE}", line_breaks=2, indent_by=indent_by)
        for row in table.rows:
            row = f"{QUOTE}, {QUOTE}".join(map(rst_escape, row))
            output_file.add_output(f"{QUOTE}{row}{QUOTE}", indent_by=indent_by)

    # Declare roles in each rST file
    # so that they are available for customization by users.
    for role in AVAILABLE_ROLES:
        output_file.add_output(f".. role:: {role}")
    if AVAILABLE_ROLES:
        output_file.blank_line()

    feature = behave.parser.parse_file(source_path)
    section(1, feature)
    description(feature)
    if feature.background and not integrate_background:
        section(2, feature.background)
        steps(feature.background.steps)
        output_file.blank_line()
    for scenario in feature.scenarios:
        section(2, scenario)
        tags(scenario.tags, feature)
        description(scenario)
        if integrate_background and feature.background:
            steps(feature.background.steps, step_format=background_step_format)
        steps(scenario.steps)
        output_file.blank_line()
        examples(scenario, feature)

    return output_file
