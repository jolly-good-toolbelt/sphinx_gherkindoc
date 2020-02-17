"""Pytest Config and shared fixtures."""
import pathlib

import pytest


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
