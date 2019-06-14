=============
Contributing
=============

Thank you for your interest in QE Tools! The following is a set of guidelines
for contributing to this project:

We use the `QE Tools SDLC Documentation`_ to define the formal SDLC process for
the project.

------------------
Ways to Contribute
------------------

If you find a bug or have an idea, `let us know`_.
We also welcome pull requests for documentation, typos, and even feature
requests.

Getting Started
---------------

After cloning this repo, simply run ``env_setup.sh``
to set up your virtual environment
and prepare your pre-commit hooks.


Submitting Pull Requests
------------------------

If you find an error in the documentation
(or anywhere that it is completely lacking),
please feel free to submit a PR to fix the error.
Did you find a **tpyo**? Submit a PR to fix that, too!

Feature implementations are also welcome,
but we encourage you to come talk to us
in the #metrics_qe_team Slack channel
to prevent duplication of effort and discuss the feature
*before* sinking too much work into it.

Review/Change Workflow
~~~~~~~~~~~~~~~~~~~~~~

* When creating a pull request, set the Reviewers to
  "QE-Tools/qe-tools-contributors".

  * PRs previously discussed with a specific person
    may be assigned to them directly to start.

* When starting to review a pull request,
  add the "In Review" label.

  * This serves as a signal that the PR is already under review
    so that if someone else wants to review,
    they know to wait until all reviewers are finished reviewing.

* Once a review is completed, remove the "In Review" label.

  * If you are requesting changes,
    assign the PR to the author.

  * If not requesting changes
    and you are the first reviewer,
    set the Reviewers to "QE-Tools/qe-tools-contributors".

  * If not requesting changes
    and you are the second reviewer,
    please merge the pull request.

* As an author,
  once requested edits are completed,
  un-assign yourself
  and assign to the reviewer requesting the changes.

  * Once assigned,
    a reviewer has 48 hours to respond to changes
    before the changes are considered approved.

  * If the change is large enough
    and other individual(s) have already reviewed,
    you may re-assign to them and ask for an additional review,
    but it is not required.

* Two approvals are preferred,
  but a single reviewer is acceptable.
  This is especially true for "trivial" pull requests such as fixing typos
  and "fast follow" PRs.

Code Standards
--------------

* The project is built using Python 3.6,
  so feel free to use any features available in this version.
* We use ``pre-commit`` to handle commit validation,
  with ``black`` for code formatting,
  and ``flake8`` for styling.
* You can manually run ``self-check.py`` any time to validate your changes
  against our checkers.
* Please include tests where appropriate.
  The coverage is lacking so any increase in coverage is appreciated.

.. _`QE Tools SDLC Documentation`: https://pages.github.rackspace.com/QualityEngineering/QE-Tools/sdlcs/README.html
.. _`let us know`: https://jira.rax.io/projects/QET/
