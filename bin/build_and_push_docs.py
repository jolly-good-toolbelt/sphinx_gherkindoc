#! /usr/bin/env python3

"""Build docs and publish to GH Pages."""
import os
import subprocess
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
subprocess.check_call(["python", f"{BASE_DIR}/build_docs.py"] + sys.argv[1:])
subprocess.check_call(["poetry", "run", "ghp-import", "-p", "docs/"])
