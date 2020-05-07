"""Tests for behave_writer module."""
import pathlib

import pytest

from sphinx_gherkindoc import writer
import rst_output_pytest


@pytest.fixture()
def feature_file_pytest(tmp_path):
    test_dir = pathlib.Path(__file__).parent
    basic_feature = test_dir / "basic_pytest.feature"
    return basic_feature


@pytest.fixture()
def raw_rst_descriptions_feature_file_pytest(tmp_path):
    test_dir = pathlib.Path(__file__).parent
    feature = test_dir / "descriptions_with_raw_rst.feature"
    return feature


@pytest.fixture()
def nobackground_feature_file_pytest(tmp_path):
    test_dir = pathlib.Path(__file__).parent
    basic_feature = test_dir / "nobackground_pytest.feature"
    return basic_feature


@pytest.fixture()
def tags_feature_file_pytest(tmp_path):
    test_dir = pathlib.Path(__file__).parent
    tags_feature = test_dir / "tags_pytest.feature"
    return tags_feature


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
def test_pytest_feature_to_rst(feature_file_pytest):
    results = pytest_writer(feature_file_pytest, feature_file_pytest.parent)
    check_with_tags(results._output, rst_output_pytest.basic_rst)


def test_pytest_nobackground_to_rst(nobackground_feature_file_pytest):
    results = pytest_writer(
        nobackground_feature_file_pytest, nobackground_feature_file_pytest.parent
    )
    check_with_tags(results._output, rst_output_pytest.no_background_rst)


def test_pytest_feature_to_rst_integrated_background(feature_file_pytest):
    results = pytest_writer(
        feature_file_pytest, feature_file_pytest.parent, integrate_background=True
    )
    check_with_tags(
        results._output, rst_output_pytest.basic_rst_with_integrated_background
    )


def test_pytest_feature_to_rst_unique_integrated_background_step_format(
    feature_file_pytest,
):
    unique_background_step_format = "{} *(Background)*"
    results = pytest_writer(
        feature_file_pytest,
        feature_file_pytest.parent,
        integrate_background=True,
        background_step_format=unique_background_step_format,
    )
    expected_output = (
        rst_output_pytest.basic_rst_unique_integrated_background_step_format
    )
    check_with_tags(results._output, expected_output)


def test_pytest_feature_to_rst_inherited_tags(tags_feature_file_pytest):
    results = pytest_writer(tags_feature_file_pytest, tags_feature_file_pytest.parent)
    check_with_tags(results._output, rst_output_pytest.tags_rst)


def test_pytest_feature_to_rst_raw_descriptions(
    raw_rst_descriptions_feature_file_pytest,
):
    results = pytest_writer(
        raw_rst_descriptions_feature_file_pytest,
        raw_rst_descriptions_feature_file_pytest.parent,
        integrate_background=True,
        raw_descriptions=True,
    )
    expected_output = rst_output_pytest.raw_rst_descriptions_rst
    check_with_tags(results._output, expected_output)
