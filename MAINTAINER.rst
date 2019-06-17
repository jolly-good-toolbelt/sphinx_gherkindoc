Maintainer's Documentation
==========================

Scripts and utilities for maintainers of this package.

Top-level scripts:
------------------

    * ``env_setup.py`` - setting up a new virtual environment.
      Uses poetry so if you like using the virtual environment poetry uses,
      you should be fine.
    * ``self_check.py`` - validates the repo is in good shape.
      Uses `pre-commit`_ but you should use ``self_check.py`` instead in case
      other things are added and as a standard entrypoint common to many repos.
    * ``run_tests.py`` - run all tests in the repo.

``bin/`` scripts:
-----------------

    * ``build_docs.py`` - build the documentation. Open ``docs/index.html`` to
      read the local docs.
    * ``build_and_push_docs.py`` - build the documentation then push to github
      pages for this repo.


.. _`pre-commit`: https://pre-commit.com/
