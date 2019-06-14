"""Configure sphinx for package doc publication."""
import os

import tomlkit

PYPROJECT_FILE = "pyproject.toml"
EXPLANATION = "- needed to extract version information."
file_path = os.path.join(
    os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir)),
    PYPROJECT_FILE,
)

try:
    with open(file_path) as f:
        toml_data = tomlkit.parse(f.read())
except FileNotFoundError as e:
    print(f"Cannot find config file {file_path} {EXPLANATION}")
    print(e)
    exit(-1)

try:
    version = str(toml_data["tool"]["poetry"]["version"])
except KeyError as e:
    print(f"The [tool.poetry] 'version' key was not found {EXPLANATION}")
    print(e)
    exit(-1)

release = version

# PLEASE EDIT THE FOLLOWING CONFIGURATION INFORMATION:
######################################################

# General information about your project.
project = "QE Common Tools - A library of shared helpers"
copyright = "2018, Rackspace Quality Engineering"  # noqa
author = "QE Engineering"

######################################################
# BELOW HERE YOU SHOULD BE ABLE TO LEAVE AS-IS.


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.inheritance_diagram",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

html_theme_options = {
    "style_external_links": True,
    "titles_only": False,
    "collapse_navigation": False,
}

source_suffix = [".rst"]

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
    if "GIT_ORIGIN_URL" not in os.environ:
        base_url = ""  # If this is non-empty, sphinx will make it clickable.
    else:
        owner_name = os.path.splitext(
            os.environ.get("GIT_ORIGIN_URL", "").split(":")[1]
        )[0]
        base_url = f"https://github.rackspace.com/{owner_name}/tree/{commit_id}"
html_context = {"build_id": commit_id, "build_url": base_url}
