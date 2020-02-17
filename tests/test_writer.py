"""Tests for writer module."""
import pytest

from sphinx_gherkindoc import writer


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
