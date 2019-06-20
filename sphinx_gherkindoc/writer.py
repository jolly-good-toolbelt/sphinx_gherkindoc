"""Helper functions for writing rST files."""
import itertools
import os
import re

import behave.parser
from qecommon_tools import display_name, get_file_contents, list_from, url_if_ticket

from .files import is_rst_file
from .glossary import step_glossary
from .utils import make_flat_name, INDENT_DEPTH, rst_escape, SphinxWriter, verbose

# The csv-table parser for restructuredtext does not allow for escaping so use
# a unicode character that looks like a quote but will not be in any Gherkin
QUOTE = "\u201C"


# IMPLEMENTATION NOTES:
# When generating rST output files from directory trees containing feature files,
# and rST/MarkDown, files, implementation concerns:
# * Walking a directory tree top down makes it hard to know if any subdirectories
#   will have interesting content worth including.
# * Walking a directory tree bottom up makes it hard to efficiently process excluded
#   directories.
#
# Strategy: Use a 2-phased approach:
# 1 Walk the directory tree top-down to avoid descending in to excluded directories.
#   Record an ordered list of places that are not excluded and thus worth looking at.
# 2 Process the recorded list in reverse order, effecting a bottom-up processing of the
#   tree, without the bottom-up concern. This way we can prune out directories that are
#   either empty or have empty children.


def toctree(path_list, subdirs, files, maxtocdepth, root_path):
    """
    Return a SphinxWriter for one level of a directory tree.

    Any rST files found at this level will have their content
    included in the TOC file instead of being referenced.
    This allows us to put content in the TOC file directly.
    The rST files that are included are expected to contain proper headers as well as
    content.
    If no rST files are included, a header is created using display_name from
    qecommon_tools.

    NOTE: If there is more than one rST file present,
          the order of their inclusion in the TOC is by filename sort order.
    """

    of = SphinxWriter()
    non_included_files = []
    need_header = True  # Track if we need to generate our own header boiler-plate.

    for a_file in sorted(files):
        if not is_rst_file(a_file):
            non_included_files.append(a_file)
            continue

        source_name_list = path_list + [a_file]
        source_name = os.path.join(*source_name_list)
        source_path = os.path.join(root_path, source_name)
        verbose("Copying content from: {}".format(source_name))
        of.add_output(get_file_contents(source_path), line_breaks=2)
        need_header = False

    if need_header:
        # We're just adding a boiler plate heading.
        temp_path_list = [root_path] + path_list if path_list else [os.curdir]
        of.create_section(1, display_name(os.path.join(*temp_path_list)))

    of.add_output(".. toctree::")
    of.add_output(
        ":maxdepth: {}".format(maxtocdepth), line_breaks=2, indent_by=INDENT_DEPTH
    )

    for a_file in sorted(non_included_files):
        # For MarkDown file content to be properly processed we
        # need toleave the file name extension unchanged.
        ext = None if a_file.lower().endswith(".md") else ""
        name = make_flat_name(path_list, filename_root=a_file, is_dir=False, ext=ext)
        of.add_output(name, indent_by=INDENT_DEPTH)

    for subdir in sorted(subdirs):
        name = make_flat_name(path_list, filename_root=subdir, is_dir=True, ext="")
        of.add_output(name, indent_by=INDENT_DEPTH)

    return of


# Simplified this from a class, for various reasons.
# Additional simplification work is needed!!!!
def feature_to_rst(source_path, root_path):
    """Return a SphinxWriter containing the rST for the given feature file."""
    output_file = SphinxWriter()

    def section(level, obj):
        section_name = u"{}: {}".format(obj.keyword, rst_escape(obj.name))
        output_file.create_section(level, section_name.rstrip(": "))

    def description(description):
        if not description:
            return
        for line in list_from(description):
            output_file.add_output(rst_escape(line), indent_by=INDENT_DEPTH)
            # Since behave strips newlines, a reasonable guess must be made as
            # to when a newline should be re-inserted
            if line[-1] == "." or line == description[-1]:
                output_file.blank_line()

    def text(text):
        if not text:
            return
        output_file.blank_line()
        output_file.add_output("::", line_breaks=2)
        # Since text blocks are treated as raw text, any new lines in the
        # Gherkin are preserved. To convert the text block into a code block,
        # each new line must be indented.
        for line in itertools.chain(*(x.splitlines() for x in list_from(text))):
            output_file.add_output(
                rst_escape(line), line_breaks=2, indent_by=INDENT_DEPTH
            )

    # Reference link here because it's too long to put inside the function itself.
    # http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#embedded-uris-and-aliases
    def ticket_url_or_tag(tag):
        """Get a URL or tag.

        If tag is a ticket, return an anonymous embedded hyperlink for it,
        else tag itself.
        """
        url = url_if_ticket(tag)
        if url:
            return "`{} <{}>`__".format(tag, url)
        return tag

    def tags(tags, *parent_objs):
        parent_with_tags = tuple(x for x in parent_objs if x.tags)
        if not (tags or parent_with_tags):
            return
        output_file.add_output(".. pull-quote::", line_breaks=2)
        tag_str = ", ".join(map(ticket_url_or_tag, tags))
        for obj in parent_with_tags:
            tags_list = ", ".join(map(ticket_url_or_tag, obj.tags))
            tag_str += u" (Inherited from {}: {} )".format(obj.keyword, tags_list)
        output_file.add_output(
            u"Tagged: {}".format(tag_str.strip()), line_breaks=2, indent_by=INDENT_DEPTH
        )

    def steps(steps):
        for step in steps:
            step_glossary[step.name.lower()].add_reference(
                step.name, os.path.relpath(step.filename, start=root_path), step.line
            )
            bold_step = re.sub(r"(\\\<.*?\>)", r"**\1**", rst_escape(step.name))
            output_file.add_output(u"- {} {}".format(step.keyword, bold_step))
            if step.table:
                output_file.blank_line()
                table(step.table, inline=True)
            if step.text:
                text(step.text)
        output_file.blank_line()

    def examples(scenario, feature):
        for example in getattr(scenario, "examples", []):
            section(3, example)
            tags(example.tags, scenario, feature)
            table(example.table)
            output_file.blank_line()

    def table(table, inline=False):
        indent_by = INDENT_DEPTH if inline else 0
        directive = ".. csv-table::"
        output_file.add_output(directive, indent_by=indent_by)
        headers = u'", "'.join(table.headings)
        indent_by += INDENT_DEPTH
        output_file.add_output(u':header: "{}"'.format(headers), indent_by=indent_by)
        output_file.add_output(
            u":quote: {}".format(QUOTE), line_breaks=2, indent_by=indent_by
        )
        for row in table.rows:
            row = u"{0}, {0}".format(QUOTE).join(map(rst_escape, row))
            output_file.add_output(u"{0}{1}{0}".format(QUOTE, row), indent_by=indent_by)

    feature = behave.parser.parse_file(source_path)
    section(1, feature)
    description(feature.description)
    if feature.background:
        section(2, feature.background)
        steps(feature.background.steps)
    for scenario in feature.scenarios:
        section(2, scenario)
        tags(scenario.tags, feature)
        description(scenario.description)
        steps(scenario.steps)
        examples(scenario, feature)

    return output_file