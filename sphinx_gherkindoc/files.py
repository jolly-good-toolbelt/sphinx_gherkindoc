"""File-related utils used throughout the module."""
import fnmatch
import os
from typing import Iterable, List, NamedTuple


# Must be lowercase.
FEATURE_FILE_SUFFIX = ".feature"
SOURCE_SUFFICIES = (FEATURE_FILE_SUFFIX, ".md", ".rst")


class DirData(NamedTuple):
    """Named tuple containing all the modified os.walk parts for a given path."""

    dir_path: str
    path_list: List[str]
    sub_dirs: List[str]
    files: List[str]


def is_feature_file(filename: str) -> bool:
    """Determine if the given filename is a feature file."""
    return filename.lower().endswith(FEATURE_FILE_SUFFIX)


def is_rst_file(filename: str) -> bool:
    """Determine if the given filename is a rST file."""
    return filename.lower().endswith(".rst")


def _not_private(filename: str) -> bool:
    """Check if a filename is private (using underscore prefix)."""
    return not filename.startswith("_")


def _is_wanted_file(filename: str) -> bool:
    """Wanted as in: We know how to process it."""
    return filename.lower().endswith(SOURCE_SUFFICIES)


def _is_excluded(filename: str, exclude_pattern_list: Iterable) -> bool:
    """Determine if the given filename should be excluded, based on the pattern list."""
    return any(map(lambda x: fnmatch.fnmatch(filename, x), exclude_pattern_list))


def _not_hidden(name: str) -> bool:
    """Determine if the filename is not hidden."""
    return not name.startswith(".")


def _wanted_source_files(files: Iterable, exclude_pattern_list: Iterable) -> List[str]:
    """Get list of wanted sorce files, excluding unwanted files."""
    wanted_files = filter(_is_wanted_file, files)
    return [
        a_file
        for a_file in wanted_files
        if not _is_excluded(a_file, exclude_pattern_list)
    ]


def scan_tree(
    starting_point: str, private: bool, exclude_patterns: Iterable
) -> List[DirData]:
    """
    Return list of entities to process, in top-down orders.

    the list can easily be processed with `.pop` to get a bottom-up
    directory ordering.
    """
    result = []

    for me, dirs, files in os.walk(os.path.abspath(starting_point)):
        if _is_excluded(me, exclude_patterns):
            dirs[:] = []
            continue

        root_path = os.path.dirname(starting_point)
        me_list = os.path.relpath(me, start=root_path).split(os.sep)

        # This prevents creating "dot" files in the output directory, which can be very
        # confusing.
        if me_list[0] == os.path.curdir:
            me_list = me_list[1:]

        # Remove all hidden directories on principle.
        # This stops scanning into version control directories such as .git, ,hg, etc.
        dirs[:] = filter(_not_hidden, dirs)

        if not private:
            dirs[:] = filter(_not_private, dirs)

        files = _wanted_source_files(files, exclude_patterns)

        result.append(DirData(me, me_list, dirs[:], files))

    return result
