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


@pytest.fixture()
def empty_feature_file(tmp_path):
    empty_feature = tmp_path / "empty.feature"
    test_dir = pathlib.Path(__file__).parent
    with open(test_dir / "empty.feature") as feature_fo:
        empty_feature.write_text(feature_fo.read())
    return empty_feature


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
    results = writer.feature_to_rst(feature_file, feature_file.parent)
    assert results._output == rst_output.basic_rst


def test_feature_to_rst_integrated_background(feature_file):
    results = writer.feature_to_rst(
        feature_file, feature_file.parent, integrate_background=True
    )
    assert results._output == rst_output.basic_rst_with_integrated_background


def test_feature_to_rst_unique_integrated_background_step_format(feature_file):
    unique_background_step_format = "{} *(Background)*"
    results = writer.feature_to_rst(
        feature_file,
        feature_file.parent,
        integrate_background=True,
        background_step_format=unique_background_step_format,
    )
    expected_output = rst_output.basic_rst_unique_integrated_background_step_format
    assert results._output == expected_output


def test_feature_to_rst_steps_converted_to_url(feature_file):
    def get_url_from_step(step):
        if step == "Given a test feature":
            return "https://github.com/jolly-good-toolbelt/sphinx_gherkindoc"

        return ""

    results = writer.feature_to_rst(
        feature_file, feature_file.parent, get_url_from_step=get_url_from_step
    )
    assert results._output == rst_output.basic_rst_with_step_url


def test_feature_to_rst_inherited_tags(tags_feature_file):
    results = writer.feature_to_rst(tags_feature_file, tags_feature_file.parent)
    assert results._output == rst_output.tags_rst


def test_feature_to_rst_tags_converted_to_url(tags_feature_file):
    def get_url_from_tag(tag):
        if "with_url" in tag:
            return "https://github.com/jolly-good-toolbelt/sphinx_gherkindoc"

        return ""

    results = writer.feature_to_rst(
        tags_feature_file, tags_feature_file.parent, get_url_from_tag=get_url_from_tag
    )
    assert results._output == rst_output.tags_rst_with_urls


def test_filter_by_tags_logic_is_triggered(tags_feature_file):
    # All the variations are tested in test_utils.test_get_all_included_scenarios,
    # so this just makes sure that logic get triggered within the writer.py module.
    results = writer.feature_to_rst(
        tags_feature_file,
        tags_feature_file.parent,
        # An include tag that should cause the feature to be excluded,
        # meaning the include/exclude helper has indeed been triggered.
        include_tags=["some-tag-no-scenario-or-feature-has"],
    )
    assert results is None


def test_empty_feature_to_rst(empty_feature_file):
    results = writer.feature_to_rst(empty_feature_file, empty_feature_file.parent)
    assert results is None
