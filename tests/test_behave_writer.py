"""Tests for behave_writer module."""
from sphinx_gherkindoc import behave_writer as writer
import rst_output


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
