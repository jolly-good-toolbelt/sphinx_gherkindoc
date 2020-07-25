"""Tests for files module."""
import pathlib

import pytest

from sphinx_gherkindoc import files


EXTENSION_LIST = (".feature", ".rst", ".md")
EXCLUDE_PATTERN_LIST = [f"*{x}" for x in EXTENSION_LIST]


@pytest.fixture(scope="module")
def tree(tmp_path_factory):
    root = tmp_path_factory.mktemp("root")
    (root / "test.feature").touch()
    (root / "_private_dir").mkdir()
    subdir = root / "subdir"
    subdir.mkdir()
    (subdir / "another_test.feature").touch()
    return root.resolve()


# files.is_feature_file
def test_is_feature_file():
    assert files.is_feature_file("test.feature") is True


def test_is_feature_file_caps():
    assert files.is_feature_file("test.FEATURE") is True


def test_is_feature_file_not():
    assert files.is_feature_file("test.py") is False


def test_is_feature_file_blank():
    assert files.is_feature_file("") is False


# files.is_rst_file
def test_is_rst_file():
    assert files.is_rst_file("test.rst") is True


def test_is_rst_file_caps():
    assert files.is_rst_file("test.RST") is True


def test_is_rst_file_not():
    assert files.is_rst_file("test.py") is False


def test_is_rst_file_blank():
    assert files.is_rst_file("") is False


# files._not_private
def test_not_private():
    assert files._not_private("test.py") is True


def test_not_private_is_private():
    assert files._not_private("_test.py") is False


def test_not_private_blank():
    assert files._not_private("") is True


# files._is_wanted_file
@pytest.mark.parametrize("extension", EXTENSION_LIST)
def test_is_wanted_file(extension):
    assert files._is_wanted_file(f"test{extension}") is True


@pytest.mark.parametrize("extension", EXTENSION_LIST)
def test_is_wanted_file_caps(extension):
    assert files._is_wanted_file(f"test{extension.upper()}") is True


def test_is_wanted_file_not():
    assert files._is_wanted_file("test.py") is False


# files._is_excluded
def test_is_excluded():
    assert files._is_excluded("test.feature", EXCLUDE_PATTERN_LIST) is True


def test_is_excluded_not():
    assert files._is_excluded("test.py", EXCLUDE_PATTERN_LIST) is False


def test_is_excluded_empty_filename():
    assert files._is_excluded("", EXCLUDE_PATTERN_LIST) is False


def test_is_excluded_empty_exclude():
    assert files._is_excluded("test.py", []) is False


def test_is_excluded_folder():
    assert files._is_excluded("subdir/test.py", ["*subdir*"]) is True


# files._not_hidden
def test_not_hidden():
    assert files._not_hidden("test.py") is True


def test_not_hidden_is():
    assert files._not_hidden(".test.py") is False


# files._wanted_source_files
def test_wanted_source_files():
    wanted_files = ["one.feature", "two.md"]
    unwanted_files = ["three.py", "subdir/four.feature"]
    assert (
        files._wanted_source_files(wanted_files + unwanted_files, ["subdir/*"])
        == wanted_files
    )


def test_wanted_source_files_empty_exclude():
    wanted_files = ["one.feature", "subdir/three.feature", "two.md"]
    unwanted_files = ["four.py"]
    assert files._wanted_source_files(wanted_files + unwanted_files, []) == wanted_files


def test_wanted_source_files_empty_files():
    assert files._wanted_source_files([], []) == []


# files.scan_tree
def test_scan_tree(tree):
    expected_data = [
        files.DirData(tree, ["root0"], ["subdir"], ["test.feature"]),
        files.DirData(
            tree / "subdir", ["root0", "subdir"], [], ["another_test.feature"]
        ),
    ]
    assert files.scan_tree(tree, False, []) == expected_data


def test_scan_tree_private(tree):
    expected_data = [
        files.DirData(tree, ["root0"], ["_private_dir", "subdir"], ["test.feature"]),
        files.DirData(tree / "_private_dir", ["root0", "_private_dir"], [], []),
        files.DirData(
            tree / "subdir", ["root0", "subdir"], [], ["another_test.feature"]
        ),
    ]
    assert files.scan_tree(tree, True, []) == expected_data


def test_scan_tree_exclude(tree):
    expected_data = [
        files.DirData(tree, ["root0"], ["_private_dir", "subdir"], ["test.feature"]),
        files.DirData(tree / "_private_dir", ["root0", "_private_dir"], [], []),
    ]
    assert files.scan_tree(tree, True, ["*subdir*"]) == expected_data


def test_scan_tree_relative():
    relative_path = pathlib.Path("tests")
    expected_data = [
        files.DirData(
            relative_path.resolve(),
            ["tests"],
            [],
            [
                "README.rst",
                "basic.feature",
                "basic_pytest.feature",
                "descriptions_with_raw_rst.feature",
                "nobackground_pytest.feature",
                "tags.feature",
                "tags_pytest.feature",
            ],
        )
    ]
    assert files.scan_tree(relative_path, False, []) == expected_data
