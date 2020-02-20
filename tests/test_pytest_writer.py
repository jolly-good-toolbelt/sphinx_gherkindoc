"""Tests for behave_writer module."""
from types import SimpleNamespace

import pytest

from sphinx_gherkindoc import writer
import rst_output


def _reformat_keywords(rst_lines):
    new_rst_lines = rst_lines[:]
    for (no_description_keyword, marker) in (("Background", "-"), ("Examples", "~")):
        line_to_match = (
            f":gherkin-{no_description_keyword.lower()}-keyword:"
            f"`{no_description_keyword}:`"
        )
        for i, line in enumerate(new_rst_lines):
            if line.startswith(line_to_match):
                new_rst_lines[i] = f"{line_to_match}\n"
            if new_rst_lines[i - 1] == f"{line_to_match}\n":
                marker_line = marker * len(line_to_match)
                new_rst_lines[i] = f"{marker_line}\n\n"
    return new_rst_lines


@pytest.fixture()
def pytest_rst_output():
    base_rst_output = SimpleNamespace()
    for attribute in dir(rst_output):
        if not attribute.startswith("_"):
            setattr(
                base_rst_output,
                attribute,
                _reformat_keywords(getattr(rst_output, attribute)),
            )
    return base_rst_output


def pytest_writer(*args, **kwargs):
    return writer.feature_to_rst(*args, **kwargs, feature_parser="pytest_bdd")


def _tagline_into_word_set(tag_line):
    return {word.strip(" ,") for word in tag_line.split() if word}


def check_with_tags(actual, expected):
    tag_text = "Tagged:"

    # pytest-bdd maintains tag data in sets, so the tag order is never guaranteed,
    # thus we have to evaluate non-tag lines for direct matching,
    #  and tag lines for all the same "words"

    # First, compare non-tag lines
    actual_without_tags = [x for x in actual if tag_text not in x]
    expected_without_tags = [x for x in expected if tag_text not in x]
    assert actual_without_tags == expected_without_tags

    # Then verify tag lines match in an orderless manner
    actual_tags = [_tagline_into_word_set(x) for x in actual if tag_text in x]
    expected_tags = [_tagline_into_word_set(x) for x in expected if tag_text in x]
    assert actual_tags == expected_tags


# writer.feature_to_rst
def test_pytest_feature_to_rst(feature_file, pytest_rst_output):
    results = pytest_writer(feature_file, feature_file.parent)
    check_with_tags(results._output, pytest_rst_output.basic_rst)


def test_pytest_feature_to_rst_integrated_background(feature_file, pytest_rst_output):
    results = pytest_writer(
        feature_file, feature_file.parent, integrate_background=True
    )
    check_with_tags(
        results._output, pytest_rst_output.basic_rst_with_integrated_background
    )


def test_pytest_feature_to_rst_unique_integrated_background_step_format(
    feature_file, pytest_rst_output
):
    unique_background_step_format = "{} *(Background)*"
    results = pytest_writer(
        feature_file,
        feature_file.parent,
        integrate_background=True,
        background_step_format=unique_background_step_format,
    )
    expected_output = (
        pytest_rst_output.basic_rst_unique_integrated_background_step_format
    )
    check_with_tags(results._output, expected_output)


def test_pytest_feature_to_rst_inherited_tags(tags_feature_file, pytest_rst_output):
    results = pytest_writer(tags_feature_file, tags_feature_file.parent)
    check_with_tags(results._output, pytest_rst_output.tags_rst)
