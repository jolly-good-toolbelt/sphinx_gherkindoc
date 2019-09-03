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

    def __gt__(self, other) -> bool:
        """Compare the location and step lenghts for the larger one."""
        return self.tuple_len() > other.tuple_len()

    def __eq__(self, other) -> bool:
        """Compare the location and step lengths for equality."""
        return self.tuple_len() == other.tuple_len()


step_glossary: DefaultDict[str, GlossaryEntry] = defaultdict(GlossaryEntry)


def make_steps_glossary(project_name: str) -> Optional[SphinxWriter]:
    """Return SphinxWriter containing the step glossary information, if any."""

    if not step_glossary:
        return None

    glossary = SphinxWriter()
    glossary.create_section(1, f"{project_name} Glossary")

    master_step_names = {
        name for gloss in step_glossary.values() for name in gloss.step_set
    }
    for term in sorted(master_step_names):
        glossary.add_output(f"- :term:`{rst_escape(term, slash_escape=True)}`")

    glossary.blank_line()
    glossary.add_output(".. glossary::")
    for entry in sorted(step_glossary.values(), reverse=True):
        for term in sorted(entry.step_set):
            glossary.add_output(
                rst_escape(term, slash_escape=True), indent_by=INDENT_DEPTH
            )

        for location, line_numbers in sorted(entry.locations.items()):
            definition = f"| {location} {', '.join(map(str, sorted(line_numbers)))}"
            glossary.add_output(definition, indent_by=INDENT_DEPTH * 2)
        glossary.blank_line()

    return glossary
