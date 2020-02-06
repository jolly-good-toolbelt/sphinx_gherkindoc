"""Generic utils used throughout the module."""
import pathlib
import string
from typing import Callable, List, Optional

import sphinx.util

# Increments of how much we indent Sphinx rST content when indenting.
INDENT_DEPTH = 4


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
