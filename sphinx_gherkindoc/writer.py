"""Helper functions for writing rST files."""
import pathlib
from typing import Callable, List, Optional

from .files import is_rst_file
from .utils import (
    display_name,
    make_flat_name,
    INDENT_DEPTH,
    SphinxWriter,
    verbose,
)

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


def toctree(
    path_list: List[str],
    subdirs: List[str],
    files: List[str],
    maxtocdepth: int,
    root_path: pathlib.Path,
    dir_display_name_parser: Optional[Callable] = None,
    display_name_from_dir: Optional[str] = None,
) -> SphinxWriter:
    """
    Return a SphinxWriter for one level of a directory tree.

    Any rST files found at this level will have their content
    included in the TOC file instead of being referenced.
    This allows us to put content in the TOC file directly.
    The rST files that are included are expected to contain proper headers as well as
    content.
    If no rST files are included, a header is created using display_name.

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
        source_name = pathlib.Path().joinpath(*source_name_list)
        source_path = root_path / source_name
        verbose(f"Copying content from: {source_name}")
        with open(source_path, "r") as source_fo:
            of.add_output(source_fo.read(), line_breaks=2)
        need_header = False

    if need_header:
        # We're just adding a boiler plate heading.
        of.create_section(
            1,
            display_name(
                root_path.joinpath(*path_list),
                dir_display_name_parser=dir_display_name_parser,
                display_name_from_dir=display_name_from_dir,
            ),
        )

    of.add_output(".. toctree::")
    of.add_output(f":maxdepth: {maxtocdepth}", line_breaks=2, indent_by=INDENT_DEPTH)

    for a_file in sorted(non_included_files):
        # For MarkDown file content to be properly processed we
        # need to leave the file name extension unchanged.
        ext = None if a_file.lower().endswith(".md") else ""
        name = make_flat_name(path_list, filename_root=a_file, is_dir=False, ext=ext)
        of.add_output(name, indent_by=INDENT_DEPTH)

    for subdir in sorted(subdirs):
        name = make_flat_name(path_list, filename_root=subdir, is_dir=True, ext="")
        of.add_output(name, indent_by=INDENT_DEPTH)

    return of
