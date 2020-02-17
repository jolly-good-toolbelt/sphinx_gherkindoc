"""Tests for behave_writer module."""
import pathlib

import pytest

from sphinx_gherkindoc import pytest_bdd_writer as writer
import rst_output as _rst_output


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


def _reformat_keywords(rst_lines):
    for (no_description_keyword, marker) in (("Background", "-"), ("Examples", "~")):
        line_to_match = (
            f":gherkin-{no_description_keyword.lower()}-keyword:"
            f"`{no_description_keyword}:`"
        )
        for i, line in enumerate(rst_lines):
            if line.startswith(line_to_match):
                rst_lines[i] = f"{line_to_match}\n"
            if rst_lines[i - 1] == f"{line_to_match}\n":
                marker_line = marker * len(line_to_match)
                rst_lines[i] = f"{marker_line}\n\n"
    return rst_lines


@pytest.fixture()
def rst_output():
    for attribute in dir(_rst_output):
        if not attribute.startswith("_"):
            setattr(
                _rst_output,
                attribute,
                _reformat_keywords(getattr(_rst_output, attribute)),
            )
    return _rst_output


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
def test_feature_to_rst(feature_file, rst_output):
    results = writer.feature_to_rst(feature_file, feature_file.parent)
    check_with_tags(results._output, rst_output.basic_rst)


def test_feature_to_rst_integrated_background(feature_file, rst_output):
    results = writer.feature_to_rst(
        feature_file, feature_file.parent, integrate_background=True
    )
    check_with_tags(results._output, rst_output.basic_rst_with_integrated_background)


def test_feature_to_rst_unique_integrated_background_step_format(
    feature_file, rst_output
):
    unique_background_step_format = "{} *(Background)*"
    results = writer.feature_to_rst(
        feature_file,
        feature_file.parent,
        integrate_background=True,
        background_step_format=unique_background_step_format,
    )
    expected_output = rst_output.basic_rst_unique_integrated_background_step_format
    check_with_tags(results._output, expected_output)


def test_feature_to_rst_inherited_tags(tags_feature_file, rst_output):
    results = writer.feature_to_rst(tags_feature_file, tags_feature_file.parent)
    check_with_tags(results._output, rst_output.tags_rst)
