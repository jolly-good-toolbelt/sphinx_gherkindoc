"""Module specific to building the steps glossary."""
from collections import defaultdict
import pathlib
from typing import DefaultDict, Optional, Set, Tuple

from .utils import INDENT_DEPTH, rst_escape, SphinxWriter


class GlossaryEntry(object):
    """Track all the different places, and by which spellings, something is used."""

    def __init__(self) -> None:
        self.step_set: Set[str] = set()
        self.locations: DefaultDict[pathlib.Path, set] = defaultdict(set)

    def add_reference(
        self, step_name: str, filename: pathlib.Path, line_number: int
    ) -> None:
        """
        Add a reference to the glossary.

        Args:
            step_name: The step name in Gherkin
            filename: The file name containing the step
            line_number: The line number containing the step

        """

        self.step_set.add(step_name)
        self.locations[filename].add(line_number)

    def tuple_len(self) -> Tuple[int, int]:
        """Get the length for each location and the number of associated steps."""
        return (len(self.locations), sum(map(len, self.locations.values())))

    def __gt__(self, other: "GlossaryEntry") -> bool:
        """Compare the location and step lenghts for the larger one."""
        return self.tuple_len() > other.tuple_len()

    def __eq__(self, other: object) -> bool:
        """Compare the location and step lengths for equality."""
        if not isinstance(other, GlossaryEntry):
            return NotImplemented
        return self.tuple_len() == other.tuple_len()


step_glossary: DefaultDict[str, GlossaryEntry] = defaultdict(GlossaryEntry)
step_glossary_grouped: DefaultDict[str, DefaultDict[str, GlossaryEntry]] = defaultdict(
    lambda: defaultdict(GlossaryEntry)
)


def make_steps_glossary(
    project_name: str, group_by: bool = False
) -> Optional[SphinxWriter]:
    """Return SphinxWriter containing the step glossary information, if any."""

    if not step_glossary and not step_glossary_grouped:
        return None

    glossary = SphinxWriter()
    glossary.create_section(1, f"{project_name} Glossary")

    if group_by:
        glossary.create_section(2, "Group By")

        for step_type, glossary_group in step_glossary_grouped.items():
            glossary.create_section(3, f"{step_type}")
            _step_glossary(glossary, glossary_group)
    else:
        _step_glossary(glossary, step_glossary)

    return glossary


def _step_glossary(
    glossary: SphinxWriter, glossary_group: DefaultDict[str, GlossaryEntry]
) -> None:
    step_names = {name for gloss in glossary_group.values() for name in gloss.step_set}
    for term in sorted(step_names):
        glossary.add_output(f"- :term:`{rst_escape(term, slash_escape=True)}`")

    glossary.blank_line()
    glossary.add_output(".. glossary::")
    for entry in sorted(glossary_group.values(), reverse=True):
        for term in sorted(entry.step_set):
            glossary.add_output(
                rst_escape(term, slash_escape=True), indent_by=INDENT_DEPTH
            )

            for location, line_numbers in sorted(entry.locations.items()):
                definition = f"| {location} {', '.join(map(str, sorted(line_numbers)))}"
                glossary.add_output(definition, indent_by=INDENT_DEPTH * 2)
            glossary.blank_line()
