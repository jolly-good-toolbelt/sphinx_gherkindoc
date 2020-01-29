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

    Scenario: Normal scenarios with add on steps (And, But)

        Given something
        And something else
        When something happens
        Then something happened
        And something else also happened
        And another thing happened

    Scenario: Indentation is ignored when any step in the scenario has text or a table

        Given a step with some text
        '''
        Here be that said text!
        '''
        And an And step with some text too
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
