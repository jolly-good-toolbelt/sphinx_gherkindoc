"""Tests for glossary module."""
from collections import defaultdict
import copy
import pathlib

import pytest

from sphinx_gherkindoc import glossary


@pytest.fixture()
def entry():
    return glossary.GlossaryEntry()


@pytest.fixture()
def step_glossary():
    old_value = copy.deepcopy(glossary.step_glossary)
    glossary.step_glossary = defaultdict(glossary.GlossaryEntry)
    glossary.step_glossary["Step one"].add_reference(
        "Step one", pathlib.Path("filename.feature"), 12
    )
    glossary.step_glossary["Step one"].add_reference(
        "Step one", pathlib.Path("filename2.feature"), 2
    )
    glossary.step_glossary["Step two"].add_reference(
        "Step two", pathlib.Path("filename.feature"), 13
    )
    yield
    glossary.step_glossary = old_value


@pytest.fixture()
def step_glossary_grouped():
    old_value = copy.deepcopy(glossary.step_glossary_grouped)
    glossary.step_glossary_grouped = defaultdict(
        lambda: defaultdict(glossary.GlossaryEntry)
    )
    glossary.step_glossary_grouped["given"]["Step one"].add_reference(
        "Step one", pathlib.Path("filename.feature"), 12
    )
    glossary.step_glossary_grouped["given"]["Step one"].add_reference(
        "Step one", pathlib.Path("filename2.feature"), 2
    )
    glossary.step_glossary_grouped["when"]["Step two"].add_reference(
        "Step two", pathlib.Path("filename.feature"), 13
    )
    yield
    glossary.step_glossary_grouped = old_value


@pytest.fixture()
def empty_step_glossary():
    old_value = copy.deepcopy(glossary.step_glossary)
    glossary.step_glossary = defaultdict(glossary.GlossaryEntry)
    yield
    glossary.step_glossary = old_value


# glossary.GlossaryEntry
def test_glossary_entry_init(entry):
    assert entry.step_set == set()
    assert entry.locations == defaultdict(list)


def test_glossary_entry_add_reference(entry):
    feature_file = pathlib.Path("filename.feature")
    entry.add_reference("A step", feature_file, 12)
    assert entry.step_set == {"A step"}
    assert dict(entry.locations) == {feature_file: {12}}


def test_glossary_entry_tuple_len(entry):
    entry.add_reference("A step", pathlib.Path("filename.feature"), 12)
    assert entry.tuple_len() == (1, 1)


@pytest.mark.usefixtures("step_glossary")
def test_glossary_gt():
    assert glossary.step_glossary["Step one"] > glossary.step_glossary["Step two"]


@pytest.mark.usefixtures("step_glossary")
def test_glossary_eq():
    assert glossary.step_glossary["Step one"] != glossary.step_glossary["Step two"]


# glossary.make_steps_glossary
@pytest.mark.usefixtures("empty_step_glossary")
def test_make_steps_glossry_empty():
    assert glossary.make_steps_glossary("Test") is None


@pytest.mark.usefixtures("step_glossary")
def test_make_steps_glossary():
    glossary_output = [
        "Test Glossary\n",
        "=============\n\n",
        "- :term:`Step one`\n",
        "- :term:`Step two`\n",
        "\n",
        ".. glossary::\n",
        "    Step one\n",
        "        | filename.feature 12\n",
        "        | filename2.feature 2\n",
        "\n",
        "    Step two\n",
        "        | filename.feature 13\n",
        "\n",
    ]
    assert glossary.make_steps_glossary("Test", group_by=False)._output == glossary_output


@pytest.mark.usefixtures("step_glossary_grouped")
def test_make_steps_glossary_group_by():
    glossary_output = [
        "Test Glossary\n",
        "=============\n\n",
        "Group By\n",
        "--------\n\n",
        "given\n",
        "~~~~~\n\n",
        "- :term:`Step one`\n",
        "\n",
        ".. glossary::\n",
        "    Step one\n",
        "        | filename.feature 12\n",
        "        | filename2.feature 2\n",
        "\n",
        "when\n",
        "~~~~\n\n",
        "- :term:`Step two`\n",
        "\n",
        ".. glossary::\n",
        "    Step two\n",
        "        | filename.feature 13\n",
        "\n",
    ]
    assert glossary.make_steps_glossary("Test", group_by=True)._output == glossary_output
