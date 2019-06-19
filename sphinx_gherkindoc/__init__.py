#!/usr/bin/env python3
"""Bring Gherkin Goodness into the Sphinx/reStructuredText (rST) world."""

from __future__ import print_function
import argparse
from collections import defaultdict
import fnmatch
import itertools
import os.path
import re
import shutil

import behave.parser
import sphinx
import sphinx.util

from qecommon_tools import display_name, get_file_contents, list_from, url_if_ticket


# DRY_RUN and VERBOSE are global states for all the code.
# By making these into global variables, the code "admits that" they are global;
# rather than cluttering up method parameters passing these values around,
# and having to track if any particular method/function needs or no-longer needs them.
DRY_RUN = False
VERBOSE = False


def verbose(message):
    """Print message only if VERBOSE, with a DRY_RUN prefix as appropriate."""
    if not VERBOSE:
        return
    if DRY_RUN:
        message = "dry-run: " + message
    print(message)


# Must be lowercase.
FEATURE_FILE_SUFFIX = ".feature"
SOURCE_SUFFICIES = (FEATURE_FILE_SUFFIX, ".md", ".rst")

# The csv-table parser for restructuredtext does not allow for escaping so use
# a unicode character that looks like a quote but will not be in any Gherkin
QUOTE = "\u201C"
_escape_mappings = {ord(x): u"\\{}".format(x) for x in ("*", '"', "#", ":", "<", ">")}
_advanced_escape_mappings = _escape_mappings.copy()
_advanced_escape_mappings[ord("\\")] = u"\\\\\\"

# Increments of how much we indent Sphinx rST content when indenting.
INDENT_DEPTH = 4

# This is a pretty arbitrary number controlling how much detail
# will show up in the various TOCs.
DEFAULT_TOC_DEPTH = 4


class SphinxWriter(object):
    """Easy Sphinx-format file creator."""

    sections = ["", "=", "-", "~", ".", "*", "+", "_", "<", ">", "/"]

    def __init__(self):
        self._output = []

    def add_output(self, line, line_breaks=1, indent_by=0):
        """Add output to be written to file.

        Args:
            line (string): The line to be written
            line_breaks(integer, optional): The number of line breaks to include
            indenty_by(integer, optional): The number of spaces to indent the line.

        """
        self._output.append(u"{}{}{}".format(" " * indent_by, line, "\n" * line_breaks))

    def blank_line(self):
        """Write a single blank line."""
        self.add_output("")

    def create_section(self, level, section):
        """Create a section of <level> (1-10 supported)."""
        self.add_output(section)
        self.add_output(self.sections[level] * len(section.rstrip()), line_breaks=2)

    def write_to_file(self, filename):
        """Write the provided output to the given filename."""
        verbose("Writing {}".format(filename))
        with sphinx.util.osutil.FileAvoidWrite(filename) as f:
            # All version of Sphinx will accept a string-type,
            # but >=2.0 accepts _only_ strings (not bytes)
            data = "".join(self._output)
            if not isinstance(data, str):
                # py3 will recognize unicode as strings natively,
                # py2 unicode needs to be encoded first
                data = data.encode("utf8")
            f.write(data)


class GlossaryEntry(object):
    """Track all the different places, and by which spellings, something is used."""

    def __init__(self):
        self.step_set = set()
        self.locations = defaultdict(list)

    def add_reference(self, step_name, filename, line_number):
        """
        Add a reference to the glossary.

        Args:
            step_name (string): The step name in Gherkin
            filename (string): The file name containing the step
            line_number (integer): The line number containing the step

        """

        self.step_set.add(step_name)
        self.locations[filename].append(line_number)

    def tuple_len(self):
        """Get the length for each location and the number of associated steps."""
        return (len(self.locations), sum(map(len, self.locations.values())))

    def __gt__(self, other):
        """Compare the location and step lenghts for the larger one."""
        return self.tuple_len() > other.tuple_len()

    def __eq__(self, other):
        """Compare the location and step lengths for equality."""
        return self.tuple_len() == other.tuple_len()


step_glossary = defaultdict(GlossaryEntry)


def make_steps_glossary(project_name):
    """Return SphinxWriter containing the step glossary information, if any."""

    if not step_glossary:
        return None

    glossary = SphinxWriter()
    glossary.create_section(1, u"{} Glossary".format(project_name))

    master_step_names = {
        name for gloss in step_glossary.values() for name in gloss.step_set
    }
    for term in sorted(master_step_names):
        glossary.add_output(u"- :term:`{}`".format(rst_escape(term, slash_escape=True)))

    glossary.blank_line()
    glossary.add_output(".. glossary::")
    for entry in sorted(step_glossary.values(), reverse=True):
        for term in sorted(entry.step_set):
            glossary.add_output(
                rst_escape(term, slash_escape=True), indent_by=INDENT_DEPTH
            )

        for location, line_numbers in sorted(entry.locations.items()):
            line_numbers = map(str, line_numbers)
            definition = u"| {}: {}".format(location, ", ".join(line_numbers))
            glossary.add_output(definition, indent_by=INDENT_DEPTH * 2)
        glossary.blank_line()

    return glossary


def rst_escape(unescaped, slash_escape=False):
    """Escape reST-ful characters to prevent parsing errors."""
    return unescaped.translate(
        _advanced_escape_mappings if slash_escape else _escape_mappings
    )


def not_private(filename):
    """Check if a filename is private (using underscore prefix)."""
    return not filename.startswith("_")


def is_rst_file(filename):
    """Determine if the given filename is a rST file."""
    return filename.lower().endswith(".rst")


def is_feature_file(filename):
    """Determine if the given filename is a feature file."""
    return filename.lower().endswith(FEATURE_FILE_SUFFIX)


def is_wanted_file(filename):
    """Wanted as in: We know how to process it."""
    return filename.lower().endswith(SOURCE_SUFFICIES)


def is_excluded(filename, exclude_pattern_list):
    """Determine if the given filename should be excluded, based on the pattern list."""
    return any(map(lambda x: fnmatch.fnmatch(filename, x), exclude_pattern_list))


def not_hidden(name):
    """Determine if the filename is not hidden."""
    return not name.startswith(".")


def wanted_source_files(files, exclude_pattern_list):
    """Get list of wanted sorce files, excluding unwanted files."""
    wanted_files = filter(is_wanted_file, files)
    return [
        a_file
        for a_file in wanted_files
        if not is_excluded(a_file, exclude_pattern_list)
    ]


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
                step.name, os.path.relpath(step.filename, root_path), step.line
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


def make_flat_name(path_list, filename_root=None, is_dir=False, ext=".rst"):
    """
    Flatten file name from a list of directories and an optional filename.

    As per notes above, this will give us a non-nested directory structure.
    """
    if filename_root is not None:
        path_list = path_list + [filename_root]
    result = ".".join(path_list)
    if ext is None:
        return result
    return result + ("-toc" if is_dir else "-file") + ext


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


def scan_tree(starting_point, private, exclude_patterns):
    """
    Return list of entities to proces, in top-down orders.

    the list can easily be processed with `.pop` to get a bottom-up
    directory ordering.
    """
    result = []

    for me, dirs, files in os.walk(os.path.abspath(starting_point)):
        if is_excluded(me, exclude_patterns):
            dirs[:] = []
            continue

        me_list = os.path.relpath(me, os.path.dirname(starting_point)).split(os.sep)

        # This prevents creating "dot" files in the output directory, which can be very
        # confusing.
        if me_list[0] == os.path.curdir:
            me_list = me_list[1:]

        # Remove all hidden directories on principle.
        # This stops scanning into version control directories such as .git, ,hg, etc.
        dirs[:] = filter(not_hidden, dirs)

        if not private:
            dirs[:] = filter(not_private, dirs)

        files = wanted_source_files(files, exclude_patterns)

        result.append((me, me_list, dirs[:], files))

    return result


def process_args(args):
    """Process the supplied CLI args."""
    work_to_do = scan_tree(args.gherkin_path, args.private, args.exclude_patterns)
    maxtocdepth = args.maxtocdepth
    output_path = args.output_path
    toc_name = args.toc_name
    step_glossary_name = args.step_glossary_name
    doc_project = args.doc_project
    root_path = os.path.dirname(os.path.abspath(args.gherkin_path))

    top_level_toc_filename = os.path.join(output_path, toc_name) + ".rst"

    non_empty_dirs = set()

    while work_to_do:
        a_dir, a_dir_list, subdirs, files = work_to_do.pop()
        new_subdirs = []
        for subdir in subdirs:
            subdir_path = os.path.join(a_dir, subdir)
            if subdir_path in non_empty_dirs:
                new_subdirs.append(subdir)

        if not (files or new_subdirs):
            continue

        non_empty_dirs.add(a_dir)

        if DRY_RUN:
            continue

        toc_file = toctree(a_dir_list, new_subdirs, files, maxtocdepth, root_path)
        # Check to see if we are at the last item to be processed
        # (which has already been popped)
        # to write the asked for master TOC file name.
        if not work_to_do:
            toc_filename = top_level_toc_filename
        else:
            toc_filename = os.path.join(
                output_path, make_flat_name(a_dir_list, is_dir=True)
            )
        toc_file.write_to_file(toc_filename)

        for a_file in files:
            a_file_list = a_dir_list + [a_file]
            source_name = os.path.join(*a_file_list)
            source_path = os.path.join(root_path, source_name)
            if is_feature_file(a_file):
                dest_name = os.path.join(
                    output_path, make_flat_name(a_file_list, is_dir=False)
                )
                feature_rst_file = feature_to_rst(source_path, root_path)
                verbose('converting "{}" to "{}"'.format(source_name, dest_name))
                feature_rst_file.write_to_file(dest_name)
            elif not is_rst_file(a_file):
                dest_name = os.path.join(
                    output_path, make_flat_name(a_file_list, is_dir=False, ext=None)
                )
                verbose('copying "{}" to "{}"'.format(source_name, dest_name))
                shutil.copy(source_path, dest_name)

    if step_glossary_name:
        glossary_filename = os.path.join(
            output_path, "{}.rst".format(step_glossary_name)
        )
        glossary = make_steps_glossary(doc_project)

        if DRY_RUN:
            verbose("No glossary generated")
            return

        if glossary is None:
            print("No steps to include in the glossary: no glossary generated")
            return

        verbose("Writing sphinx glossary: {}".format(glossary_filename))
        glossary.write_to_file(glossary_filename)


def main():
    """Convert a directory-tree of Gherking Feature files to rST files."""
    description = (
        "Look recursively in <gherkin_path> for Gherkin files and create one "
        "reST file for each. Other rST files found along the way will be included "
        "as prologue content above each TOC."
    )
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("gherkin_path", help="Directory to search for Gherkin files")
    parser.add_argument("output_path", help="Directory to place all output")
    parser.add_argument(
        "exclude_patterns",
        nargs="*",
        help="file and/or directory patterns that will be excluded",
    )
    parser.add_argument(
        "-d",
        "--maxtocdepth",
        type=int,
        default=DEFAULT_TOC_DEPTH,
        help="Maximum depth of submodules to show in the TOC",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Run the script without creating files",
    )
    parser.add_argument(
        "-P", "--private", action="store_true", help='Include "_private" folders'
    )
    parser.add_argument("-N", "--toc-name", help="File name for TOC", default="gherkin")
    parser.add_argument(
        "-H", "--doc-project", help="Project name (default: root module name)"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Silence any output to screen"
    )
    parser.add_argument(
        "-G",
        "--step-glossary-name",
        default=None,
        help="Include steps glossary under the given name."
        " If not specified, no glossary will be created.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print files created and actions taken",
    )
    parser.add_argument(
        "--version", action="store_true", help="Show version information and exit"
    )

    args = parser.parse_args()

    if args.version:
        parser.exit(
            message="Sphinx (sphinx-gherkindoc) {}".format(sphinx.__display_version__)
        )

    if args.dry_run:
        global DRY_RUN
        DRY_RUN = True

    if args.verbose:
        global VERBOSE
        VERBOSE = True

    if args.doc_project is None:
        args.doc_project = os.path.abspath(args.gherkin_path).split(os.path.sep)[-1]

    if not os.path.isdir(args.gherkin_path):
        parser.error("{} is not a directory.".format(args.gherkin_path))

    args.output_path = os.path.abspath(args.output_path)
    if not os.path.isdir(args.output_path):
        if not DRY_RUN:
            verbose("creating directory: {}".format(args.output_path))
            os.makedirs(args.output_path)

    process_args(args)


def config():
    """Emit a customized version of the sample sphinx config file."""
    description = (
        "Create a default Sphinx configuration for producing nice"
        " Gherkin-based documentation"
    )
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "project_name", default="Your Project Name Here", help="Name of your project"
    )
    parser.add_argument(
        "author", default="Your Team Name Here", help="Directory to place all output"
    )
    parser.add_argument("--version", default="", help="version of your project, if any")
    parser.add_argument("--release", default="", help="release of your project, if any")
    args = parser.parse_args()

    substitutions = {
        "%%PROJECT%%": args.project_name,
        "%%AUTHOR%%": args.author,
        "%%VERSION%%": args.version,
        "%%RELEASE%%": args.release,
    }
    source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    sample_contents = get_file_contents(source_dir, "sample-conf.py")
    for old_value, new_value in substitutions.items():
        sample_contents = sample_contents.replace(old_value, new_value)

    print(sample_contents)


if __name__ == "__main__":
    main()
