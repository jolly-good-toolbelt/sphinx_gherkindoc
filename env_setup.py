#!/usr/bin/env python3
"""
Setup the development environment.

Runs the following commands:
    {}
"""
import argparse
import os
import shlex
import subprocess

__commands_to_run = [
    "poetry run pip install --upgrade pip<19",
    "poetry install",
    "poetry run pre-commit install",
]

__doc__ = __doc__.format("\n    ".join(__commands_to_run))


def execute_command_list(commands_to_run, verbose=True):
    """
    Execute each command in the list.

    If any command fails, print a helpful message and exit with that status.
    """
    for command in commands_to_run:
        if verbose:
            print(command)
        subprocess.run(shlex.split(command), check=True)


def env_setup(verbose):
    """Prepare environment for running."""
    print(f"In: {os.getcwd()}")
    if os.getenv("VIRTUAL_ENV"):
        print(f"Setting up Virtual Environment: {os.environ['VIRTUAL_ENV']}")
    print()
    execute_command_list(__commands_to_run)


def main():
    """Execute env_setup using command line args."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="show each command before it is executed",
    )
    args = parser.parse_args()
    env_setup(args.verbose)


if __name__ == "__main__":
    main()
