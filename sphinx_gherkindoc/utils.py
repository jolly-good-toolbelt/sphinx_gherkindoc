"""Generic utils used throughout the module."""
import sphinx.util

# Increments of how much we indent Sphinx rST content when indenting.
INDENT_DEPTH = 4


# DRY_RUN and VERBOSE are global states for all the code.
# By making these into global variables, the code "admits that" they are global;
# rather than cluttering up method parameters passing these values around,
# and having to track if any particular method/function needs or no-longer needs them.
DRY_RUN = False
VERBOSE = False


def verbose(message):
    """Print message only if VERBOSE, with a DRY_RUN prefix as appropriate."""
    if not VERBOSE:
        return
    if DRY_RUN:
        message = "dry-run: " + message
    print(message)


# Build up dictionary of characters that need escaping
_escape_mappings = {ord(x): u"\\{}".format(x) for x in ("*", '"', "#", ":", "<", ">")}
_advanced_escape_mappings = _escape_mappings.copy()
_advanced_escape_mappings[ord("\\")] = u"\\\\\\"


def rst_escape(unescaped, slash_escape=False):
    """Escape reST-ful characters to prevent parsing errors."""
    return unescaped.translate(
        _advanced_escape_mappings if slash_escape else _escape_mappings
    )


def make_flat_name(path_list, filename_root=None, is_dir=False, ext=".rst"):
    """
    Flatten file name from a list of directories and an optional filename.

    As per notes above, this will give us a non-nested directory structure.
    """
    if filename_root is not None:
        path_list = path_list + [filename_root]
    result = ".".join(path_list)
    if ext is None:
        return result
    return result + ("-toc" if is_dir else "-file") + ext


class SphinxWriter(object):
    """Easy Sphinx-format file creator."""

    sections = ["", "=", "-", "~", ".", "*", "+", "_", "<", ">", "/"]

    def __init__(self):
        self._output = []

    def add_output(self, line, line_breaks=1, indent_by=0):
        """Add output to be written to file.

        Args:
            line (string): The line to be written
            line_breaks(integer, optional): The number of line breaks to include
            indenty_by(integer, optional): The number of spaces to indent the line.

        """
        self._output.append(u"{}{}{}".format(" " * indent_by, line, "\n" * line_breaks))

    def blank_line(self):
        """Write a single blank line."""
        self.add_output("")

    def create_section(self, level, section):
        """Create a section of <level> (1-10 supported)."""
        self.add_output(section)
        self.add_output(self.sections[level] * len(section.rstrip()), line_breaks=2)

    def write_to_file(self, filename):
        """Write the provided output to the given filename."""
        verbose("Writing {}".format(filename))
        with sphinx.util.osutil.FileAvoidWrite(filename) as f:
            # All version of Sphinx will accept a string-type,
            # but >=2.0 accepts _only_ strings (not bytes)
            data = "".join(self._output)
            if not isinstance(data, str):
                # py3 will recognize unicode as strings natively,
                # py2 unicode needs to be encoded first
                data = data.encode("utf8")
            f.write(data)
