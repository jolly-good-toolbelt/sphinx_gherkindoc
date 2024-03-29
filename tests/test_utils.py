"""Tests for utils module."""
import pytest

from sphinx_gherkindoc import utils


TEST_MESSAGE = "This is a test message"
PATH_LIST = ["a", "b", "c"]
PATH_ROOT = ".".join(PATH_LIST)
ESCAPE_LIST = ("*", '"', "#", ":", "<", ">")


@pytest.fixture()
def constants():
    dry_run = utils.DRY_RUN
    verbose = utils.VERBOSE
    yield
    utils.set_dry_run(dry_run)
    utils.set_verbose(verbose)


# Ensure that a new test dir is created for every test,
# since some tests may add/rename files.
@pytest.fixture(scope="function")
def display_name_tree(tmp_path_factory):
    root = tmp_path_factory.mktemp("root")
    display_name_path = root / "display_name_test"
    display_name_path.mkdir()
    return display_name_path.resolve()


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


@pytest.mark.parametrize("char", ESCAPE_LIST)
def test_rst_escape_nonslash(char):
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


# utils.display_name
def test_display_name_folder(display_name_tree):
    assert utils.display_name(display_name_tree) == "Display Name Test"


def test_display_name_package(display_name_tree):
    assert utils.display_name(display_name_tree, "a.b.package_name") == "Package Name"


def test_display_name_file(display_name_tree):
    display_name_file = display_name_tree / "display_name.txt"
    display_name_file.write_text("Fancy Display Name")
    assert utils.display_name(display_name_tree) == "Fancy Display Name"


def test_display_name_file_and_package(display_name_tree):
    display_name_file = display_name_tree / "display_name.txt"
    display_name_file.write_text("Fancy Display Name")
    assert utils.display_name(display_name_tree, "a.b.c") == "Fancy Display Name"


def test_display_name_dir_converter(display_name_tree):
    def dir_name_to_display_name(dir_name: str):
        return dir_name.upper().replace("_", " ")

    assert (
        utils.display_name(
            display_name_tree, dir_display_name_converter=dir_name_to_display_name
        )
        == "DISPLAY NAME TEST"
    )


# Basic objects with only the attributes needed for `get_all_included_scenarios`
# Can't use @dataclass since we run tests with older versions of python than 3.7
class Feature:
    """Bare minimum test feature class."""

    def __init__(self, tags, scenarios):
        self.tags = tags
        self.scenarios = scenarios


class Scenario:
    """Bare minimum test scenario class."""

    def __init__(self, tags, examples):
        self.tags = tags
        self.examples = examples


class Example:
    """Bare minimum test examples table class."""

    def __init__(self, tags):
        self.tags = tags


arbitrary_multiple_number = 4
tagless_scenarios = [
    Scenario(tags=[], examples=[]) for _ in range(arbitrary_multiple_number)
]
feature_tagged_with_a = Feature(scenarios=tagless_scenarios, tags=["a"])
feature_tagged_with_a_and_b = Feature(scenarios=tagless_scenarios, tags=["a", "b"])
scenarios_tagged_with_a = [
    Scenario(tags=["a"], examples=[]) for _ in range(arbitrary_multiple_number)
]
scenarios_tagged_with_b = [
    Scenario(tags=["b"], examples=[]) for _ in range(arbitrary_multiple_number)
]
scenarios_tagged_with_a_and_b = [
    Scenario(tags=["a", "b"], examples=[]) for _ in range(arbitrary_multiple_number)
]
examples_tagged_with_a = [Example(tags=["a"]) for _ in range(arbitrary_multiple_number)]
examples_tagged_with_b = [Example(tags=["b"]) for _ in range(arbitrary_multiple_number)]


@pytest.mark.parametrize(
    "description, feature, include_tags, exclude_tags, expected_scenarios",
    [
        # ~ ONLY FEATURE TAGS ~
        (
            "Feature is included if no include or exclude tags are provided",
            feature_tagged_with_a,
            None,
            None,
            feature_tagged_with_a.scenarios,
        ),
        (
            "Feature tagged with an include tag is included",
            feature_tagged_with_a,
            ["a"],
            None,
            feature_tagged_with_a.scenarios,
        ),
        (
            "Feature tagged with a non-exclude tag is included",
            feature_tagged_with_a,
            None,
            ["b"],
            feature_tagged_with_a.scenarios,
        ),
        (
            "Feature tagged with an include tag but not an include tag is included",
            feature_tagged_with_a,
            ["a"],
            ["b"],
            feature_tagged_with_a.scenarios,
        ),
        (
            "Feature tagged with a non-include tag is excluded",
            feature_tagged_with_a,
            ["b"],
            None,
            [],
        ),
        (
            "Feature tagged with an exclude tag is excluded",
            feature_tagged_with_a,
            None,
            ["a"],
            [],
        ),
        (
            "Feature tagged with an exclude tag and an include tag is excluded",
            feature_tagged_with_a_and_b,
            ["a"],
            ["b"],
            [],
        ),
        # ~ ONLY SCENARIO TAGS ~
        (
            "All scenarios tagged with include are included",
            Feature([], scenarios_tagged_with_a),
            ["a"],
            None,
            scenarios_tagged_with_a,
        ),
        (
            "All scenarios tagged with exclude cause no included scenarios",
            Feature([], scenarios_tagged_with_a),
            None,
            ["a"],
            [],
        ),
        (
            "All scenarios tagged with both include and exclude "
            "cause no included scenarios",
            Feature([], scenarios_tagged_with_a_and_b),
            ["a"],
            ["b"],
            [],
        ),
        (
            "Only scenarios tagged with an include tag are included",
            Feature([], scenarios_tagged_with_a + scenarios_tagged_with_b),
            ["a"],
            None,
            scenarios_tagged_with_a,
        ),
        (
            "Only scenarios tagged with an exclude tag are excluded",
            Feature([], scenarios_tagged_with_a + scenarios_tagged_with_b),
            None,
            ["a"],
            scenarios_tagged_with_b,
        ),
        # ~ FEATURE & SCENARIO TAGS ~
        (
            "When a feature is tagged with an include tag, "
            "only scenarios tagged with an exclude tag are excluded",
            Feature(["a"], scenarios_tagged_with_a + scenarios_tagged_with_b),
            None,
            ["b"],
            scenarios_tagged_with_a,
        ),
        (
            "When a feature is tagged with exclude tag, "
            "but scenarios have include tag, "
            "then no scenarios are included",
            Feature(["b"], scenarios_tagged_with_a + scenarios_tagged_with_b),
            ["a"],
            ["b"],
            [],
        ),
        # ~ EXAMPLES TABLES TAGS ~
        (
            "Specific examples tables can be excluded",
            Feature(
                tags=["a"],
                scenarios=[
                    Scenario(
                        tags=[],
                        examples=examples_tagged_with_a + examples_tagged_with_b,
                    )
                ],
            ),
            ["a"],
            ["b"],
            [Scenario(tags=[], examples=examples_tagged_with_a)],
        ),
        (
            "Scenarios with include tag, but with all examples tables "
            "having an exclude tag will exclude the whole scenario",
            Feature(
                tags=["a"],
                scenarios=[Scenario(tags=[], examples=examples_tagged_with_b)],
            ),
            ["a"],
            ["b"],
            [],
        ),
        (
            "Scenario is included if only an examples table has an include tag",
            Feature(
                tags=[],
                scenarios=[
                    Scenario(
                        tags=[],
                        examples=examples_tagged_with_a + examples_tagged_with_b,
                    )
                ],
            ),
            ["a"],
            ["b"],
            [Scenario(tags=[], examples=examples_tagged_with_a)],
        ),
    ],
)
def test_get_all_included_scenarios(
    description, feature, include_tags, exclude_tags, expected_scenarios
):
    actual_scenarios = utils.get_all_included_scenarios(
        feature, include_tags, exclude_tags
    )
    err_msg = "Test Failed: {}".format(description)

    # We can't just do `assert actual_scenarios == expected_scenarios`,
    # because sometimes they are technically different test objects,
    # but they have the same len, values, etc.
    # It would be hard to set that up in the tests because the
    # `utils.get_all_included_scenarios` function can mutate scenario objects.

    assert len(actual_scenarios) == len(expected_scenarios), err_msg

    for i in range(len(actual_scenarios)):
        expected_scenario = expected_scenarios[i]
        actual_scenario = actual_scenarios[i]

        assert actual_scenario.tags == expected_scenario.tags, err_msg
        if hasattr(expected_scenario, "examples"):
            assert actual_scenario.examples == expected_scenario.examples, err_msg
