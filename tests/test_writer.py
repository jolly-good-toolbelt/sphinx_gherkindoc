"""Tests for writer module."""
import pathlib

import pytest

from sphinx_gherkindoc import writer
import rst_output


@pytest.fixture(scope="module")
def feature_tree(tmp_path_factory):
    root = tmp_path_factory.mktemp("feature_root")
    (root / "test.feature").touch()
    (root / "readme.rst").write_text("Read me first")
    (root / "_private_dir").mkdir()
    subdir = root / "subdir"
    subdir.mkdir()
    (subdir / "another_test.feature").touch()
    return root.resolve()


@pytest.fixture()
def feature_file(tmp_path):
    basic_feature = tmp_path / "basic.feature"
    test_dir = pathlib.Path(__file__).parent
    with open(test_dir / "basic.feature") as feature_fo:
        basic_feature.write_text(feature_fo.read())
    return basic_feature


@pytest.fixture()
def tags_feature_file(tmp_path):
    tags_feature = tmp_path / "tags.feature"
    test_dir = pathlib.Path(__file__).parent
    with open(test_dir / "tags.feature") as feature_fo:
        tags_feature.write_text(feature_fo.read())
    return tags_feature


# writer.toctree
def test_toctree(feature_tree):
    expected_results = [
        "Root0\n",
        "=====\n\n",
        ".. toctree::\n",
        "    :maxdepth: 2\n\n",
        "    root0.test.feature-file\n",
    ]
    results = writer.toctree(["root0"], [], ["test.feature"], 2, feature_tree.parent)
    assert results._output == expected_results


def test_toctree_with_rst(feature_tree):
    expected_results = [
        "Read me first\n\n",
        ".. toctree::\n",
        "    :maxdepth: 2\n\n",
        "    feature_root0.test.feature-file\n",
    ]
    results = writer.toctree(
        ["feature_root0"], [], ["test.feature", "readme.rst"], 2, feature_tree.parent
    )
    assert results._output == expected_results


def test_toctree_with_subdir(feature_tree):
    expected_results = [
        "Root0\n",
        "=====\n\n",
        ".. toctree::\n",
        "    :maxdepth: 2\n\n",
        "    root0.test.feature-file\n",
        "    root0.subdir-toc\n",
    ]
    results = writer.toctree(
        ["root0"], ["subdir"], ["test.feature"], 2, feature_tree.parent
    )
    assert results._output == expected_results


# writer.feature_to_rst
def test_feature_to_rst(feature_file):
    results = writer.feature_to_rst(str(feature_file), feature_file.parent)
    assert results._output == rst_output.basic_rst


def test_feature_to_rst_inherited_tags(tags_feature_file):
    results = writer.feature_to_rst(str(tags_feature_file), tags_feature_file.parent)
    assert results._output == rst_output.tags_rst
