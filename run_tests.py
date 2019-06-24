#!/usr/bin/env python3
"""
Run all available tests.

Runs the following commands:
    {}
"""
import argparse

from env_setup import execute_command_list

__commands_to_run = [
    "poetry run pytest -vv --cov sphinx_gherkindoc --cov-report term-missing"
]


__doc__ = __doc__.format("\n    ".join(__commands_to_run))


def run_tests(do_setup=False, self_check=False, verbose=True):
    """Run code checks."""
    if self_check:
        __commands_to_run.insert(0, "python self_check.py")
    if do_setup:
        __commands_to_run.insert(0, "python env_setup.py")

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
        "--check",
        action="store_true",
        help='run "./self_check.py" before running self checks',
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="do not show each command before it is executed",
    )
    args = parser.parse_args()

    run_tests(do_setup=args.setup, self_check=args.check, verbose=not args.quiet)


if __name__ == "__main__":
    main()
