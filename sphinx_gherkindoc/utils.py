"""Generic utils used throughout the module."""
import pathlib
import string
from typing import Callable, List, Optional

import sphinx.util

from sphinx_gherkindoc.parsers import ScenarioClass, FeatureClass, ExamplesTableClass

# Increments of how much we indent Sphinx rST content when indenting.
INDENT_DEPTH = 4


MAIN_STEP_KEYWORDS = ["Given", "When", "Then"]

# The csv-table parser for restructuredtext does not allow for escaping so use
# a unicode character that looks like a quote but will not be in any Gherkin
QUOTE = "\u201C"


# DRY_RUN and VERBOSE are global states for all the code.
# By making these into global variables, the code "admits that" they are global;
# rather than cluttering up method parameters passing these values around,
# and having to track if any particular method/function needs or no-longer needs them.
DRY_RUN = False
VERBOSE = False


def verbose(message: str) -> None:
    """Print message only if VERBOSE, with a DRY_RUN prefix as appropriate."""
    if not VERBOSE:
        return
    if DRY_RUN:
        message = "dry-run: " + message
    print(message)


def set_dry_run(value: bool) -> None:
    """Set the value for DRY_RUN outside this module."""
    global DRY_RUN
    DRY_RUN = value


def set_verbose(value: bool) -> None:
    """Set the value for VERBOSE outside this module."""
    global VERBOSE
    VERBOSE = value


# Build up dictionary of characters that need escaping
_escape_mappings = {ord(x): f"\\{x}" for x in ("*", '"', "#", ":", "<", ">")}
_advanced_escape_mappings = _escape_mappings.copy()
_advanced_escape_mappings[ord("\\")] = "\\\\\\"


def rst_escape(unescaped: str, slash_escape: bool = False) -> str:
    """
    Escape reST-ful characters to prevent parsing errors.

    Args:
        unescaped: A string that potentially contains characters needing escaping
        slash_escape: if True, escape slashes found in ``unescaped``

    Returns:
        A string which has reST-ful characters appropriately escaped

    """
    return unescaped.translate(
        _advanced_escape_mappings if slash_escape else _escape_mappings
    )


def make_flat_name(
    path_list: List[str],
    filename_root: str = None,
    is_dir: bool = False,
    ext: Optional[str] = ".rst",
) -> str:
    """
    Build a flat file name from the provided information.

    Args:
        path_list: Directory hierarchy to flatten
        filename_root: If provided, the root of the filename to flatten (no extension)
        is_dir: If True, mark the new filename as a table of contents
        ext: Optional extension for the new file name

    Returns:
        A filename containing the full path, separated by periods

    """
    if filename_root is not None:
        path_list = path_list + [filename_root]
    result = ".".join(path_list)
    if ext is None:
        return result
    return result + ("-toc" if is_dir else "-file") + ext


class SphinxWriter(object):
    """Easy Sphinx-format file creator."""

    sections = ["", "=", "-", "~", ".", "*", "+", "_", "<", ">", "/"]

    def __init__(self) -> None:
        self._output: List[str] = []

    def add_output(self, line: str, line_breaks: int = 1, indent_by: int = 0) -> None:
        """Add output to be written to file.

        Args:
            line: The line to be written
            line_breaks: The number of line breaks to include
            indenty_by: The number of spaces to indent the line.
        """
        line_breaks_str = "\n" * line_breaks
        self._output.append(f"{' ' * indent_by}{line}{line_breaks_str}")

    def blank_line(self) -> None:
        """Write a single blank line."""
        self.add_output("")

    def create_section(self, level: int, section: str) -> None:
        """
        Create a reST-formatted section header based on the provided level.

        Args:
            level: The level depth of the section header (1-10 supported)
            section: The section title
        """
        self.add_output(section)
        self.add_output(self.sections[level] * len(section.rstrip()), line_breaks=2)

    def write_to_file(self, filename: pathlib.Path) -> None:
        """Write the provided output to the given filename.

        Args:
            filename: The full path to write the output
        """
        verbose(f"Writing {filename}")
        with sphinx.util.osutil.FileAvoidWrite(filename) as f:
            # All version of Sphinx will accept a string-type,
            # but >=2.0 accepts _only_ strings (not bytes)
            f.write("".join(self._output))


def display_name(
    path: pathlib.Path,
    package_name: Optional[str] = "",
    dir_display_name_converter: Optional[Callable] = None,
) -> str:
    """
    Create a human-readable name for a given project.

    Determine the display name for a project given a path and (optional) package name.
    If a display_name.txt file is found, the first line is returned. Otherwise, return a
    title-cased string from either the base directory or package_name (if provided).

    Args:
        path: Path for searching
        package_name: Sphinx-style, dot-delimited package name (optional)
        dir_display_name_converter: A function for converting a dir to a display name.

    Returns:
        A display name for the provided path

    """
    name_path = path / "display_name.txt"
    if name_path.exists():
        with open(name_path, "r") as name_fo:
            return name_fo.readline().rstrip("\r\n")

    raw_name = package_name.split(".")[-1] if package_name else path.name

    if dir_display_name_converter:
        return dir_display_name_converter(raw_name)

    return string.capwords(raw_name.replace("_", " "))


def _examples_table_if_included(
    examples_table: ExamplesTableClass,
    scenario_has_include_tag: bool,
    include_tags_set: set,
    exclude_tags_set: set,
) -> Optional[ExamplesTableClass]:
    """Return an examples table if it should be included."""
    examples_table_tags_set = set(examples_table.tags)
    examples_table_has_include_tag = bool(examples_table_tags_set & include_tags_set)

    if any(
        # Exclude the examples table if:
        [
            # Examples table has an exclude tag
            (examples_table_tags_set & exclude_tags_set),
            # Neither the scenario,
            # nor any scenario outline examples tables
            # have an include tag
            (not scenario_has_include_tag and not examples_table_has_include_tag),
        ]
    ):
        return None

    return examples_table


def _scenario_if_included(
    scenario: ScenarioClass,
    feature_has_include_tag: bool,
    include_tags_set: set,
    exclude_tags_set: set,
) -> Optional[ScenarioClass]:
    """Return a (possibly modified) scenario if it should be included."""
    scenario_tags_set = set(scenario.tags)
    scenario_examples = getattr(scenario, "examples", [])

    # If there are no include tags,
    # then treat it the same as if the scenario has an include tag.
    # If include tags exist, that will affect whether or not
    # any examples tables need to have an include tag.
    # If the feature has an include tag, then the scenario inherits it.
    scenario_has_include_tag = feature_has_include_tag or (
        bool(scenario_tags_set & include_tags_set) if include_tags_set else True
    )

    included_examples = list(
        filter(
            None,
            (
                _examples_table_if_included(
                    examples_table,
                    scenario_has_include_tag,
                    include_tags_set,
                    exclude_tags_set,
                )
                for examples_table in scenario_examples
            ),
        )
    )

    # This is the default, even if the scenario has no examples tables.
    all_examples_tables_have_exclude_tag = False
    if scenario_examples:
        all_examples_tables_have_exclude_tag = all(
            (set(examples_table.tags) & exclude_tags_set)
            for examples_table in scenario_examples
        )

    at_least_one_examples_table_included = scenario_examples and included_examples
    if any(
        # Exclude if:
        [
            # Scenario has an exclude tag
            (scenario_tags_set & exclude_tags_set),
            # Neither the scenario, nor any scenario examples tables are included
            (not scenario_has_include_tag and not at_least_one_examples_table_included),
            # All examples tables in the scenario have at least one exclude tag
            all_examples_tables_have_exclude_tag,
        ]
    ):
        return None

    # Only include examples tables that are included
    if scenario_examples:
        scenario.examples = included_examples

    return scenario


def get_all_included_scenarios(
    feature: FeatureClass,
    include_tags: List[str] = None,
    exclude_tags: List[str] = None,
) -> List[ScenarioClass]:
    """
    Get all scenarios to include in the docs based on the include/exclude tags.

    This is designed to match what tests would be run if you ran a test suite
    with something like this (pytest-bdd format)::

        -m include_this_tag -m "not exclude_this_tag"

    Args:
        feature: The feature whose scenarios are to be filtered.
        include_tags: Tags for which scenarios should be included.
        exclude_tags: Tags for which scenarios should be excluded.

    Returns:
         All scenarios to include.

    """
    # If there's no exclude/include logic return all scenarios
    if not include_tags and not exclude_tags:
        return feature.scenarios

    include_tags_set = set(include_tags) if include_tags else set()
    exclude_tags_set = set(exclude_tags) if exclude_tags else set()
    feature_tags_set = set(feature.tags)

    if feature_tags_set & exclude_tags_set:
        return []

    # If there are no include tags,
    # then treat it the same as if the feature has an include tag.
    # If include tags exist, that will affect whether or not
    # the scenario needs to have an include tag.
    feature_has_include_tag = (
        bool(feature_tags_set & include_tags_set) if include_tags else True
    )

    return list(
        filter(
            None,
            (
                _scenario_if_included(
                    scenario,
                    feature_has_include_tag,
                    include_tags_set,
                    exclude_tags_set,
                )
                for scenario in feature.scenarios
            ),
        )
    )
