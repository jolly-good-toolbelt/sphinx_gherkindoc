#!/usr/bin/env python3
"""
Script to make sure the repo is good enough for running tests, meets SDLC, etc.

Basically, antyhing you want to put here that will be part of your automated
PR checking and whatever santiy checking you want for the CICD server to be confident
that it can start a test run without any missing packages, syntax errors, etc.

We're leaning in to using 'pre-commit' but this script can still be used
to run or check things that aren't a good fit for 'pre-commit'.

Runs the following commands:
    {}
"""
import argparse

from env_setup import execute_command_list

SETUP_COMMAND = "python ./env_setup.py"

# Fill in with your own project details!!!
__commands_to_run = ["poetry run pre-commit run -a"]

__doc__ = __doc__.format("\n    ".join(__commands_to_run))


def self_check(do_setup=False, verbose=True):
    """Run code checks."""
    if do_setup:
        __commands_to_run.insert(0, SETUP_COMMAND)

    execute_command_list(__commands_to_run, verbose=verbose)


def main():
    """Self check with cli args."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=__doc__
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help='run "./env_setup.py" before running self checks',
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="do not show each command before it is executed",
    )
    args = parser.parse_args()

    self_check(do_setup=args.setup, verbose=not args.quiet)


if __name__ == "__main__":
    main()
