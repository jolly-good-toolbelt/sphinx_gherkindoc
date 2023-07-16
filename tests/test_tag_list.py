"""Tests for tag list."""
import pytest
import copy
from sphinx_gherkindoc import tag_management


@pytest.fixture()
def tag_list():
    old_value = copy.deepcopy(tag_management.tag_set)
    tag_management.tag_set = {"Tag1", "Tag2", "Tag3"}
    yield
    tag_management.tag_set = old_value


def test_tag_list_output(tag_list):
    tag_list_output = [
        "Test Tag List\n",
        "=============\n\n",
        "* Tag1\n",
        "\n",
        "* Tag2\n",
        "\n",
        "* Tag3\n",
        "\n",
    ]
    assert tag_list_output == tag_management.make_tag_list("Test")._output
