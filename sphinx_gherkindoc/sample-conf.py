"""Sample Sphinx config file for use with behave-based testing repositories."""

import os


# PLEASE EDIT THE FOLLOWING CONFIGURATION INFORMATION:

# General information about your project.
project = "%%PROJECT%%"
copyright = "2018, Rackspace Quality Engineering"  # noqa
author = "%%AUTHOR%%"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = "%%VERSION%%"

# The full version, including alpha/beta/rc tags.
release = "%%RELEASE%%"

# BELOW HERE YOU SHOULD BE ABLE TO LEAVE AS-IS.


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

from recommonmark.parser import CommonMarkParser  # noqa

source_parsers = {".md": CommonMarkParser}
source_suffix = [".rst", ".md"]

# The master toctree document.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    ".tox",
    "*/.tox",
    ".eggs",
    "*/.eggs",
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

# If anyone wants to use another theme, they can change that here,
# but we consider that expert Sphinx user territory.
import sphinx_rtd_theme  # noqa

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

commit_id = os.environ.get("ghprbPullId") or os.environ.get("GIT_COMMIT_ID")
base_url = os.environ.get("ghprbPullLink")
if not base_url:
    owner_name = os.environ.get("GIT_ORIGIN_URL", "")
    if not owner_name:
        base_url = ""  # If this is non-empty, sphinx will make it clickable.
    else:
        owner_name = os.path.splitext(owner_name.split(":")[1])[0]
        base_url = "https://github.rackspace.com/{}/tree/{}".format(
            owner_name, commit_id
        )
html_context = {"build_id": commit_id, "build_url": base_url}
