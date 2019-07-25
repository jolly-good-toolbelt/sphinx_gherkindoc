Feature: Integrated Backgrounds

  Background:
    Given a step that is from the background
    But the step actually appears with the scenario steps in the sphinx docs

  Scenario: First Scenario
    Given a step that is defined in the scenario
    And one more for good measure
    When I use sphinx-gherkindoc with the --integrate-background flag
    Then the background steps should be integrated with the scenario steps

  Scenario: Second Scenario
    Given a step from scenario 2 that is defined in the scenario
    And one more from scenario 2 for good measure
    When I use sphinx-gherkindoc with the --integrate-background flag
    Then the background steps should be integrated with the scenario steps
