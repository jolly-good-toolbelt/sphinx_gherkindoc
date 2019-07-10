sphinx-gherkindoc
=================

``sphinx-gherkindoc`` brings Gherkin goodness
into the Sphinx/reStructuredText (rST) world.

Why should I use it?
--------------------

**Share your requirements with your larger team.**
Gherkin makes it easy for anyone to read requirements.
Sphinx makes Gherkin pretty enough to be readable.
``sphinx-gherkindoc`` handles converting flat-text feature files
into easy to read documents you won't cringe to share with your larger team.

**Easily see what steps you have and where you are using them.**
``sphinx-gherkindoc`` can create a glossary of your steps.
This helps makes it easy to:

   * find steps to reuse
   * notice similar steps that might be duplicates or unintended variations
   * see patterns that you might exploit to reduce the number of steps you have
   * find out where and which feature files would be affected
     if a step's wording or implementation changes


How does it do that?
--------------------

``sphinx-gherkindoc`` recursively scans a given directory
to find all the feature and markup files,
and converts them into files
that can be included in Sphinx-based documentation.
This script was inspired by ``sphinx-apidoc``
which does a similar thing for source code.

.. Note::

    This tool only creates the rST inputs for a sphinx document run,
    you still need to fit these files
    in to your larger documentation building process yourself.

For specific details on the command line options,
please consult the ``--help`` output.
Most command line options mirror their counterpart in ``sphinx-apidoc``.

For the most basic usage, an input (``<gherkin_path>``)
and output (``<output_path>``) path must be provided.
The files put in to the ``<output_path>``
can be incorporated into any larger documentation,
created by any means.

Additionally, a list of ``fnmatch``-compatible patterns can be added
to the command line,
to indicate directories to be excluded from processing.

One notable addition is the step glossary(``-G``, ``--step-glossary``).
The step glossary command line option causes ``sphinx-gherkindoc``
to create the named file in the ``<output_path>`` directory.
The step glossary content is formatted into two lists:

   * A list of all the steps found, in alphabetical order.
     Each item in this list is a link to its details in the second list.
   * A list of the steps showing the file names and line numbers
     where they are used.
     This list is in order by the most number of uses first.


How are my files converted?
---------------------------

When scanning the ``<gherkin_path>`` directory tree,
``sphinx-gherkindoc`` will do the following:

   * Feature files found
     are processed into rST files in the ``<output_path>`` directory.
   * Directories will be converted to Sphinx Table of Contents (TOC) files that
     link to any feature files in the same directory,
     and to any TOC files from direct subdirectories.
   * Any rST files found in a directory have their contents copied
     to the front of the TOC file for that directory.
     If more than one rST file is found in a directory,
     they are processed in sort order.
   * If no rST files are found in a directory,
     then a header for the TOC is created based
     on the contents of a ``display_name.txt`` file, if present,
     or the name of the directory.
   * Any MarkDown (md) files are referenced
     from the TOC file for the directory they are in.
   * Directories with no feature, rST, or md files are pruned,
     recursively upwards.


The meat'n'potatoes will be your feature files.
Put rST files next to your feature files
to present context and additional helpful material.
If any rST files are in the same directory,
they should also contain any appropriate headers
and other such formatting.
``sphinx-gherkindoc`` will only create (minimal) headers when
there are no rST files present at all.


Examples
--------

Disclaimer: This `is not` a tutorial on how to use or configure Sphinx.
It `is` some common ways you can use ``sphinx-gherkindoc``
as part of your documentation generation.
Reminder if you skipped all that stuff above:
``--help`` will show you the default values
when command line options aren't used.

Conventions - Sphinx-based document production usually uses two directories:

    * ``_docs`` - the working directory where we put all the rST files
      from the various tools as we are building documents.
      This directory shoud not be checked in to version control
      and should only contain files created by a documentation run.
    * ``docs`` - the output directory for a documentation run.
      For example, this is where ``index.html`` is found
      when building HTML docs, etc.
      This directory should not be checked in to version control
      as it contains only derived and processed files.


1. Convert feature files to rST;
   process all feature and document files
   in/under ``feature/root/directory-here`` into the ``_docs`` directory
   using all the defaults::

       sphinx-gherkindoc feature/root/directory-here _docs

2. Same as above,
   but also create a step glossary file ``my_step_glossary`` in ``_docs``::

       sphinx-gherkindoc -G my_step_glossary feature/root/directory-here _docs

3. Experiment!
Once you have the 2nd step working
and integrated in to your document building process,
you may find you want to tweak the results some.
It's a lot easier to do that `after` you have the basic process working.
Experiment with the other optional parameters
to get the effect(s) you want.

Special Instructions for Tag Links
----------------------------------

Any tag can be converted into an anonymous link
via a plugin or command-line argument.
The converter needs to be a single function
that accepts a single string parameter, the tag,
and returns a URL if the tag should include a link
or an empty string if not.

In order to register the plugin for a ``poetry``-based project::

    [tools.poetry.plugins."parsers"]
    url = "my_custom_library.parse:optional_url_from_tag"

In order to register the plugin for a ``setup.py``-based project::

    setup(
        ...
        entry_points={
            'parsers': ['url = my_custom_library.parse:optional_url_from_tag']
        }
    )

In order to use the parser via command line,
the ``--url_from-tag`` flag should be used.
The provided string should be be formatted ``<library>:<method_name>``
