Feature: Testing Sphinx Writer

    Test the ability to write Gherkin data to a SphinxWriter object

    Background: Some requirements for this test
        Given that this file exists

    @quarantined @JIRA-1234
    Scenario: Test a Scenario

        A scenario is quicker to write than a outline but less robust.

        Given a test feature
        When the suite reaches a scenario
        Then the file is converted into rST

    Scenario Outline: Test a Scenario Outline

        Given I put <thing> in a blender
        When I turn the blender on
        Then it should transform into <other thing>

        Examples: Fruit
            | thing  | other thing |
            | apple  | apple sauce |
            | banana | smoothie    |

    Scenario: Text and Table Scenario

        Test the additional options for a scenario

        Given step text
        '''
        Lorum ipsum solor sit amet.
        '''
        When the suite reaches a scenario table
            | name      | department  |
            | Barry     | Beer Cans   |
            | Pudey     | Silly Walks |
            | Two-Lumps | Silly Walks |
        Then the file is converted into rST

    Scenario: Indentation For Secondary Step Keywords

        Given something not indented
        And something else that IS indented
        When something not indented happens
        Then something not indented happened
        And something indented also happened
        And another indented thing happened

    Scenario: Indentation For Secondary Step Keywords With Text and Tables

        Given some text for a non-indented step
        '''
        Here be that said text!
        '''
        And some test for a step that IS indented
        '''
        Hello again!
        '''
        And how about a table in there too
            | position | name         |
            | first    | Who          |
            | second   | What         |
            | third    | I don't know |
        When the fantasy has ended
        And all the children are gone
        Then something deep inside me
        '''
        Helps me to carry on
        '''
        And Encarnaciooooon
        And doodle-doodle-doodle-doo
