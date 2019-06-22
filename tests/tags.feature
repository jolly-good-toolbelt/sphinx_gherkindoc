@positive
Feature: Testing Sphinx Writer

  Test the ability to write Gherkin data to a SphinxWriter object

  Background: Some requirements for this test
    Given that this file exists

  @api
  Scenario: Test a Scenario

    A scenario is quicker to write than a outline but less robust.

    Given a test feature
    When the suite reaches a scenario
    Then the file is converted into rST
