"""Tests for glossary module."""
from collections import defaultdict
import copy

import pytest

from sphinx_gherkindoc import glossary


@pytest.fixture()
def entry():
    return glossary.GlossaryEntry()


@pytest.fixture()
def step_glossary():
    old_value = copy.deepcopy(glossary.step_glossary)
    glossary.step_glossary["Step one"].add_reference("Step one", "filename.feature", 12)
    glossary.step_glossary["Step one"].add_reference("Step one", "filename2.feature", 2)
    glossary.step_glossary["Step two"].add_reference("Step two", "filename.feature", 13)
    yield
    glossary.step_glossary = old_value


# glossary.GlossaryEntry
def test_glossary_entry_init(entry):
    assert entry.step_set == set()
    assert entry.locations == defaultdict(list)


def test_glossary_entry_add_reference(entry):
    entry.add_reference("A step", "filename.feature", 12)
    assert entry.step_set == {"A step"}
    assert dict(entry.locations) == {"filename.feature": [12]}


def test_glossary_entry_tuple_len(entry):
    entry.add_reference("A step", "filename.feature", 12)
    assert entry.tuple_len() == (1, 1)


@pytest.mark.usefixtures("step_glossary")
def test_glossary_gt():
    assert glossary.step_glossary["Step one"] > glossary.step_glossary["Step two"]


@pytest.mark.usefixtures("step_glossary")
def test_glossary_eq():
    assert (
        glossary.step_glossary["Step one"] == glossary.step_glossary["Step two"]
    ) is False


# glossary.make_step_glossary
def test_make_step_glossry_empty():
    assert glossary.make_steps_glossary("Test") is None


@pytest.mark.usefixtures("step_glossary")
def test_make_step_glossry():
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
    assert glossary.make_steps_glossary("Test")._output == glossary_output
