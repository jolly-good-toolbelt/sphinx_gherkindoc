"""Pytest Config and shared fixtures."""
import shutil
import pathlib

import pytest


@pytest.fixture()
def feature_file(tmp_path):
    basic_feature = tmp_path / "basic.feature"
    test_dir = pathlib.Path(__file__).parent
    shutil.copyfile(test_dir / "basic.feature", basic_feature)
    return basic_feature


@pytest.fixture()
def tags_feature_file(tmp_path):
    tags_feature = tmp_path / "tags.feature"
    test_dir = pathlib.Path(__file__).parent
    shutil.copyfile(test_dir / "tags.feature", tags_feature)
    return tags_feature
