"""File-related utils used throughout the module."""
import fnmatch
import os
import pathlib
from typing import Iterable, List, NamedTuple


# Must be lowercase.
FEATURE_FILE_SUFFIX = ".feature"
SOURCE_SUFFICIES = (FEATURE_FILE_SUFFIX, ".md", ".rst")


class DirData(NamedTuple):
    """Named tuple containing all the modified os.walk parts for a given path."""

    dir_path: pathlib.Path
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
    return sorted(
        a_file
        for a_file in wanted_files
        if not _is_excluded(a_file, exclude_pattern_list)
    )


def scan_tree(
    starting_point: pathlib.Path, private: bool, exclude_patterns: Iterable
) -> List[DirData]:
    """
    Return list of entities to process, in top-down orders.

    the list can easily be processed with `.pop` to get a bottom-up
    directory ordering.
    """
    result = []

    # Do not assume an absolute path is provided
    starting_point = starting_point.resolve()
    for me, dirs, files in os.walk(starting_point):
        if _is_excluded(me, exclude_patterns):
            dirs[:] = []
            continue

        # Remove all hidden directories on principle.
        # This stops scanning into version control directories such as .git, ,hg, etc.
        dirs[:] = filter(_not_hidden, dirs)

        if not private:
            dirs[:] = filter(_not_private, dirs)

        # Make recursion predictable by sorting directory entries since
        # os.walk doesn't make any guarantees about the order it uses.
        dirs.sort()

        me_path = pathlib.Path(me)
        result.append(
            DirData(
                me_path,
                [str(x) for x in me_path.relative_to(starting_point.parent).parts],
                dirs[:],
                _wanted_source_files(files, exclude_patterns),
            )
        )

    return result
