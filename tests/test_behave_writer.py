"""Tests for behave_writer module."""
import pathlib

import pytest

from sphinx_gherkindoc import behave_writer as writer
import rst_output


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


def test_feature_to_rst_inherited_tags(tags_feature_file):
    results = writer.feature_to_rst(tags_feature_file, tags_feature_file.parent)
    assert results._output == rst_output.tags_rst
