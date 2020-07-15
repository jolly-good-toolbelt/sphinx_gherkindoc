#!/usr/bin/env python3
"""Module for running the tool from the CLI."""
import argparse
import importlib
import pkg_resources
import pathlib
import shutil
from typing import Callable, Set

import sphinx

from .files import is_feature_file, is_rst_file, scan_tree
from .glossary import make_steps_glossary
from .parsers import parsers
from .utils import make_flat_name, set_dry_run, set_verbose, verbose
from .writer import feature_to_rst, toctree

# This is a pretty arbitrary number controlling how much detail
# will show up in the various TOCs.
DEFAULT_TOC_DEPTH = 4


def _get_function_from_command_line_arg(module_func_str: str) -> Callable:
    """Get a function from a module:func string that comes from a command arg.

    The ``module_func_str`` must be in the form ``{module_name}:{function_name}``.

    :param module_func_str: The string containing the module and function names.
    :return: The imported python function based on the given string.
    """
    module_name, function_name = module_func_str.split(":", maxsplit=1)
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


def process_args(
    args: argparse.Namespace,
    gherkin_path: pathlib.Path,
    output_path: pathlib.Path,
    doc_project: str,
) -> None:
    """Process the supplied CLI args."""
    work_to_do = scan_tree(gherkin_path, args.private, args.exclude_patterns)
    maxtocdepth = args.maxtocdepth
    toc_name = args.toc_name
    step_glossary_name = args.step_glossary_name
    doc_project = args.doc_project
    root_path = gherkin_path.resolve().parent

    top_level_toc_filename = output_path / f"{toc_name}.rst"

    non_empty_dirs: Set[pathlib.Path] = set()

    get_url_from_tag = None
    get_url_from_step = None
    dir_display_name_converter = None
    # Set parsers once and pass along where they are needed.
    for entry_point in pkg_resources.iter_entry_points("parsers"):
        # `url` is a supported legacy key value for the `tag_url`.
        if entry_point.name in ("url", "tag_url"):
            get_url_from_tag = entry_point.load()

        if entry_point.name == "step_url":
            get_url_from_step = entry_point.load()

        if entry_point.name == "dir_display_name":
            dir_display_name_converter = entry_point.load()

    # Override parsers if there is a command line arg
    if args.url_from_tag:
        get_url_from_tag = _get_function_from_command_line_arg(args.url_from_tag)

    if args.url_from_step:
        get_url_from_step = _get_function_from_command_line_arg(args.url_from_step)

    if args.display_name_from_dir:
        dir_display_name_converter = _get_function_from_command_line_arg(
            args.display_name_from_dir
        )

    while work_to_do:
        current = work_to_do.pop()
        new_subdirs = []
        for subdir in current.sub_dirs:
            subdir_path = pathlib.Path() / current.dir_path / subdir
            if subdir_path in non_empty_dirs:
                new_subdirs.append(subdir)

        if not (current.files or new_subdirs):
            continue

        non_empty_dirs.add(current.dir_path)

        if args.dry_run:
            continue

        toc_file = toctree(
            current.path_list,
            new_subdirs,
            current.files,
            maxtocdepth,
            root_path,
            dir_display_name_converter=dir_display_name_converter,
        )
        # Check to see if we are at the last item to be processed
        # (which has already been popped)
        # to write the asked for master TOC file name.
        if not work_to_do:
            toc_filename = top_level_toc_filename
        else:
            toc_filename = output_path / make_flat_name(current.path_list, is_dir=True)
        toc_file.write_to_file(toc_filename)

        for a_file in current.files:
            a_file_list = current.path_list + [a_file]
            source_name = pathlib.Path().joinpath(*a_file_list)
            source_path = root_path / source_name
            if is_feature_file(a_file):
                dest_name = output_path / make_flat_name(a_file_list, is_dir=False)
                feature_rst_file = feature_to_rst(
                    source_path,
                    root_path,
                    feature_parser=args.parser,
                    get_url_from_tag=get_url_from_tag,
                    get_url_from_step=get_url_from_step,
                    integrate_background=args.integrate_background,
                    background_step_format=args.background_step_format,
                    raw_descriptions=args.raw_descriptions,
                    include_tags=args.include_tags,
                    exclude_tags=args.exclude_tags,
                )
                if not feature_rst_file:
                    continue

                verbose(f'converting "{source_name}" to "{dest_name}"')
                feature_rst_file.write_to_file(dest_name)
            elif not is_rst_file(a_file):
                dest_name = output_path / make_flat_name(
                    a_file_list, is_dir=False, ext=None
                )
                verbose(f'copying "{source_name}" to "{dest_name}"')
                shutil.copy(source_path, dest_name)

    if step_glossary_name:
        glossary_filename = output_path / f"{step_glossary_name}.rst"
        glossary = make_steps_glossary(doc_project)

        if args.dry_run:
            verbose("No glossary generated")
            return

        if glossary is None:
            print("No steps to include in the glossary: no glossary generated")
            return

        verbose(f"Writing sphinx glossary: {glossary_filename}")
        glossary.write_to_file(glossary_filename)


def main() -> None:
    """Convert a directory-tree of Gherkin Feature files to rST files."""
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
        "--integrate-background",
        action="store_true",
        help=(
            "Remove all references to Background, "
            "and integrate the steps into each scenario."
        ),
    )
    parser.add_argument(
        "--background-step-format",
        default="{}",
        help=(
            "A format string to use to format integrated background steps. "
            "It should contain a single pair of empty curly braces, "
            "which is where the contents of the background step will go. "
            "NOTE: This flag is only relevant when the --integrate-background flag "
            "is also included."
        ),
    )
    parser.add_argument(
        "--parser",
        default="behave",
        choices=list(parsers.keys()),
        help=f"Specify an alternate parser to use.",
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
    url_help = (
        "A library and method name to call to build a URL from a tag. The string"
        " should be <library>:<method_name> and it should accept a single string"
        " parameter, the tag."
    )
    parser.add_argument("--url-from-tag", help=url_help)
    step_url_help = (
        "A library and method name to call to build a URL from a step. The string"
        " should be <library>:<method_name> and it should accept a single string"
        " parameter, the step name."
    )
    parser.add_argument("--url-from-step", help=step_url_help)
    display_name_from_dir_help = (
        "A library and method name to call to convert a directory name into a"
        " display name. The string should be <library>:<method_name>"
        " and it should accept a single string parameter, the directory name."
        " The output of this function will be the same as creating"
        " display_name.txt files for each directory, based on the directory name."
        " Any display_name.txt files that exist will take precedence over this flag."
    )
    parser.add_argument("--display-name-from-dir", help=display_name_from_dir_help)
    parser.add_argument(
        "--raw-descriptions",
        action="store_true",
        help=(
            "Treat text from feature and scenario descriptions as raw rST. "
            "This allows descriptions to contain rST links, code blocks, etc."
        ),
    )
    include_exclude_tags_caveat = (
        "If a feature/scenario has both an exclude and and include tag,"
        "it will be excluded."
    )
    exclude_tags_help = (
        "Features and scenarios tagged with these exclude tags "
        "will not be included in the build docs. " + include_exclude_tags_caveat
    )
    parser.add_argument("--exclude-tags", help=exclude_tags_help, nargs="*")
    include_tags_help = (
        "Only features and scenarios tagged with at least one of these include tags "
        "will be included in the build docs." + include_exclude_tags_caveat
    )
    parser.add_argument("--include-tags", help=include_tags_help, nargs="*")

    args = parser.parse_args()

    if args.version:
        parser.exit(message=f"Sphinx (sphinx-gherkindoc) {sphinx.__display_version__}")

    set_dry_run(args.dry_run)
    set_verbose(args.verbose)

    gherkin_path = pathlib.Path(args.gherkin_path)
    if not gherkin_path.is_dir():
        parser.error(f"{args.gherkin_path} is not a directory.")

    if args.doc_project is None:
        args.doc_project = gherkin_path.parts[-1]

    output_path = pathlib.Path(args.output_path).resolve()
    if not output_path.is_dir():
        if not args.dry_run:
            verbose(f"creating directory: {args.output_path}")
            output_path.mkdir(parents=True)

    process_args(args, gherkin_path, output_path, args.doc_project)


def config() -> None:
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
    source_dir = pathlib.Path(__file__).resolve().parent
    with open(source_dir / "sample-conf.py", "r") as conf_fo:
        sample_contents = conf_fo.read()
    for old_value, new_value in substitutions.items():
        sample_contents = sample_contents.replace(old_value, new_value)

    print(sample_contents)


if __name__ == "__main__":
    main()
