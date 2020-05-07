#! /usr/bin/env python3

"""Build the documentation for this package."""
import argparse
import glob
import os
import shutil
import subprocess


# Assumption: This script lives in a directory
# that is one level down from the root of the repo:
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# NOTE: 'git rev-parse --show-toplevel' would work from anywhere.
#       We are doing git commands "anyways", but I am not sure how much git-ness we want
#       to bake into this script...

DOCS_OUTPUT_DIRECTORY = "docs"
DOCS_WORKING_DIRECTORY = "_docs"


def main():
    """Build the docs."""
    # Setup environment variables
    commit_id = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=BASE_DIR, universal_newlines=True
    )
    os.environ["GIT_COMMIT_ID"] = commit_id.rstrip("\n")

    origin_url = subprocess.check_output(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=BASE_DIR,
        universal_newlines=True,
    )
    os.environ["GIT_ORIGIN_URL"] = origin_url.rstrip("\n")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dirty",
        action="store_true",
        help="Leave the output directory untouched before starting to build documents",
    )
    args = parser.parse_args()

    if not args.dirty:
        shutil.rmtree(DOCS_OUTPUT_DIRECTORY, ignore_errors=True)
        shutil.rmtree(DOCS_WORKING_DIRECTORY, ignore_errors=True)

    sphinx_apidoc_cmd = [
        "poetry",
        "run",
        "sphinx-apidoc",
        "--output-dir",
        DOCS_WORKING_DIRECTORY,
        "--no-toc",
        "--force",
        "--module-first",
    ]
    print("Building API docs")
    subprocess.check_call(
        sphinx_apidoc_cmd + ["sphinx_gherkindoc", "*sample-conf*"], cwd=BASE_DIR
    )

    print("Building Sample Gherkin docs")
    subprocess.check_call(
        [
            "poetry",
            "run",
            "sphinx-gherkindoc",
            "--doc-project",
            "Sample Gherkin",
            "--toc-name",
            "sample-gherkindoc",
            "--step-glossary-name",
            "sample-gherkindoc-glossary",
            "--parser",
            "pytest_bdd",
            "--raw-descriptions",
            "tests",
            DOCS_WORKING_DIRECTORY,
        ]
    )
    subprocess.check_call(
        [
            "poetry",
            "run",
            "sphinx-gherkindoc",
            "--doc-project",
            "Sample Gherkin With Integrated Background",
            "--toc-name",
            "sample-gherkindoc-integrated-background-default",
            "tests_for_integrated_background/default_format",
            DOCS_WORKING_DIRECTORY,
            "--integrate-background",
        ]
    )
    unique_background_step_format = "{} *(Background)*"
    subprocess.check_call(
        [
            "poetry",
            "run",
            "sphinx-gherkindoc",
            "--doc-project",
            "Sample Gherkin With Integrated Background "
            "And A Unique Background Step Format",
            "--toc-name",
            "sample-gherkindoc-integrated-background-unique-format",
            "tests_for_integrated_background/unique_format",
            DOCS_WORKING_DIRECTORY,
            "--integrate-background",
            "--background-step-format",
            unique_background_step_format,
        ]
    )

    # Copy over all the top level rST files so we don't
    # have to keep a duplicate list here.
    for filename in glob.iglob("*.rst"):
        shutil.copy(filename, DOCS_WORKING_DIRECTORY)

    for filename in glob.iglob(os.path.join("sphinx_docs", "*")):
        shutil.copy(filename, DOCS_WORKING_DIRECTORY)

    os.environ["PYTHONPATH"] = os.path.curdir
    subprocess.check_call(
        [
            "poetry",
            "run",
            "sphinx-build",
            "-c",
            DOCS_WORKING_DIRECTORY,
            "-aEW",
            DOCS_WORKING_DIRECTORY,
            DOCS_OUTPUT_DIRECTORY,
        ],
        cwd=BASE_DIR,
    )


if __name__ == "__main__":
    main()
