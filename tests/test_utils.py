"""Tests for utils module."""
import pytest

from sphinx_gherkindoc import utils


TEST_MESSAGE = "This is a test message"
PATH_LIST = ["a", "b", "c"]
PATH_ROOT = ".".join(PATH_LIST)


@pytest.fixture()
def constants():
    dry_run = utils.DRY_RUN
    verbose = utils.VERBOSE
    yield
    utils.set_dry_run(dry_run)
    utils.set_verbose(verbose)


@pytest.fixture()
def writer():
    return utils.SphinxWriter()


# utils.set_dry_run
@pytest.mark.usefixtures("constants")
def test_set_dry_run_true():
    utils.set_dry_run(True)
    assert utils.DRY_RUN is True


@pytest.mark.usefixtures("constants")
def test_set_dry_run_false():
    utils.set_dry_run(False)
    assert utils.DRY_RUN is False


# utils.set_verbose
@pytest.mark.usefixtures("constants")
def test_set_verbose_true():
    utils.set_verbose(True)
    assert utils.DRY_RUN is False


@pytest.mark.usefixtures("constants")
def test_set_verbose_false():
    utils.set_verbose(False)
    assert utils.DRY_RUN is False


# utils.verbose
def test_verbose_unmodified(capsys):
    utils.verbose(TEST_MESSAGE)
    assert capsys.readouterr().out == ""


@pytest.mark.usefixtures("constants")
def test_verbose_verbose(capsys):
    utils.set_verbose(True)
    utils.verbose(TEST_MESSAGE)
    assert capsys.readouterr().out == f"{TEST_MESSAGE}\n"


@pytest.mark.usefixtures("constants")
def test_verbose_dry_run(capsys):
    utils.set_dry_run(True)
    utils.verbose(TEST_MESSAGE)
    assert capsys.readouterr().out == ""


@pytest.mark.usefixtures("constants")
def test_verbose_dry_run_verbose(capsys):
    utils.set_dry_run(True)
    utils.set_verbose(True)
    utils.verbose(TEST_MESSAGE)
    assert capsys.readouterr().out == f"dry-run: {TEST_MESSAGE}\n"


# utils.rst_escape
def test_rst_escape_unmodified():
    assert utils.rst_escape(TEST_MESSAGE) == TEST_MESSAGE


def test_rst_escape_nonslash():
    for char in ("*", '"', "#", ":", "<", ">"):
        assert utils.rst_escape(char) == f"\\{char}"


def test_rst_escape_unmodified_slash():
    assert utils.rst_escape("\\") == "\\"


def test_rst_escape_modified_slash():
    assert utils.rst_escape("\\", slash_escape=True) == "\\\\\\"


# utils.make_flat_name
def test_make_flat_name():
    assert utils.make_flat_name(PATH_LIST) == f"{PATH_ROOT}-file.rst"


def test_make_flat_name_with_filename_root():
    flat_name = utils.make_flat_name(PATH_LIST, filename_root="root")
    assert flat_name == f"{PATH_ROOT}.root-file.rst"


def test_make_flat_name_is_dir():
    flat_name = utils.make_flat_name(PATH_LIST, is_dir=True)
    assert flat_name == f"{PATH_ROOT}-toc.rst"


def test_make_flat_name_extension():
    ext = ".txt"
    flat_name = utils.make_flat_name(PATH_LIST, ext=ext)
    assert flat_name == f"{PATH_ROOT}-file{ext}"


def test_make_flat_name_empty_extension():
    flat_name = utils.make_flat_name(PATH_LIST, ext="")
    assert flat_name == f"{PATH_ROOT}-file"


def test_make_flat_name_none_extension():
    flat_name = utils.make_flat_name(PATH_LIST, ext=None)
    assert flat_name == PATH_ROOT


def test_make_flat_name_none_is_dir_extension():
    flat_name = utils.make_flat_name(PATH_LIST, is_dir=True, ext=None)
    assert flat_name == PATH_ROOT


# utils.SphinxWriter
@pytest.mark.usefixtures("writer")
def test_sphinxwriter_init(writer):
    assert writer._output == []


@pytest.mark.usefixtures("writer")
def test_sphinxwriter_blank_line(writer):
    writer.blank_line()
    assert writer._output == ["\n"]


@pytest.mark.usefixtures("writer")
def test_sphinxwriter_create_section(writer):
    level = 1
    writer.create_section(level, TEST_MESSAGE)
    expected_output = [
        f"{TEST_MESSAGE}\n",
        f"{writer.sections[level] * len(TEST_MESSAGE)}\n\n",
    ]
    assert writer._output == expected_output


@pytest.mark.usefixtures("writer")
def test_sphinxwriter_create_section_large(writer):
    with pytest.raises(IndexError):
        writer.create_section(11, TEST_MESSAGE)


@pytest.mark.usefixtures("writer")
def test_sphinxwriter_create_section_empty(writer):
    level = 1
    writer.create_section(level, "")
    expected_output = ["\n", "\n\n"]
    assert writer._output == expected_output


@pytest.mark.usefixtures("writer")
def test_sphinxwriter_add_output(writer):
    writer.add_output(TEST_MESSAGE)
    assert writer._output == [f"{TEST_MESSAGE}\n"]


@pytest.mark.usefixtures("writer")
def test_sphinxwriter_add_output_line_breaks(writer):
    line_breaks = 10
    writer.add_output(TEST_MESSAGE, line_breaks=line_breaks)
    line_break_str = "\n" * line_breaks
    assert writer._output == [f"{TEST_MESSAGE}{line_break_str}"]


@pytest.mark.usefixtures("writer")
def test_sphinxwriter_add_output_line_breaks_negative(writer):
    writer.add_output(TEST_MESSAGE, line_breaks=-1)
    assert writer._output == [TEST_MESSAGE]


@pytest.mark.usefixtures("writer")
def test_sphinxwriter_add_output_indent_by(writer):
    indent_by = 10
    writer.add_output(TEST_MESSAGE, indent_by=indent_by)
    assert writer._output == [f"{' ' * indent_by}{TEST_MESSAGE}\n"]


@pytest.mark.usefixtures("writer")
def test_sphinxwriter_add_output_indent_by_negative(writer):
    writer.add_output(TEST_MESSAGE, indent_by=-1)
    assert writer._output == [f"{TEST_MESSAGE}\n"]


@pytest.mark.usefixtures("writer")
def test_sphinxwriter_add_output_blank(writer):
    writer.add_output("")
    assert writer._output == ["\n"]


@pytest.mark.usefixtures("writer")
def test_sphinxwriter_add_output_blank_line_breaks(writer):
    line_breaks = 10
    writer.add_output("", line_breaks=line_breaks)
    line_break_str = "\n" * line_breaks
    assert writer._output == [f"{line_break_str}"]


@pytest.mark.usefixtures("writer")
def test_sphinxwriter_write_to_file(writer, tmpdir):
    filename = tmpdir.join("test.txt")
    writer.add_output(TEST_MESSAGE)
    writer.write_to_file(filename)
    assert filename.read() == f"{TEST_MESSAGE}\n"


@pytest.mark.usefixtures("writer")
def test_sphinxwriter_write_to_file_bad_path(writer, tmpdir):
    writer.add_output(TEST_MESSAGE)
    with pytest.raises(FileNotFoundError):
        writer.write_to_file("/This/path/does/not/exist")


@pytest.mark.usefixtures("constants", "writer")
def test_sphinxwriter_write_to_file_verbose(writer, tmpdir, capsys):
    utils.set_verbose(True)
    filename = tmpdir.join("test.txt")
    writer.add_output(TEST_MESSAGE)
    writer.write_to_file(filename)
    assert capsys.readouterr().out == f"Writing {filename}\n"
