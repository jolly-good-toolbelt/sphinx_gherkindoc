Feature: Descriptions with raw rST
  Sometimes we want to describe a feature, but it is also helpful to
  put in a code block like this:

  .. code-block::

          North
      West  *  East
          South

  Or sometimes we may want to put in a link to something
  like `Python <http://www.python.org/>`__.

  Scenario: A scenario can be described with rST too
    We might want the same thing in a scenario.

    .. code-block::

            North
        West  *  East
            South

    Or sometimes we may want to put in a link to something
    like `Python <http://www.python.org/>`__.

    Given a
    When b
    Then c
