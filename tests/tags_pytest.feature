@positive
Feature: Testing Sphinx Writer

  Test the ability to write Gherkin data to a SphinxWriter object

  Background: Some requirements for this test
    Given that this file exists

  @api @tag_with_url
  Scenario: Test a Scenario

    Given a test feature
    When the suite reaches a scenario
    Then the file is converted into rST
