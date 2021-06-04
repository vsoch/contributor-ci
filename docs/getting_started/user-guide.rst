.. _getting_started-user-guide:

==========
User Guide
==========

Contributor CI was created with the intention to help measure collaboration in
one or more repositories or an organization over time.
If you haven't read :ref:`getting_started-installation` you should do that first.


Really Quick Start
==================

TODO

.. code-block:: console

    # install contributor ci
    $ pip install contributor-ci

    # Export a GitHub Personal Access Token
    $ export GITHUB_TOKEN=xxxxxxxxxxxxxx

    # See metric extractors available
    $ cci list
    
    # Run an extraction
    $ cci extract repos



Quick Start
===========

TOOD

.. code-block:: console


.. _getting_started-config:


Configuration
=============

Since the majority of the command line interactions should be automated, we
use a main configuration file called ``contributor-ci.yaml``, that is
looked for in the present working directory where you call the client.
A simple example is shown here:

.. code-block:: console

    # The output directory to create a structure of results
    # defaults to $PWD/.cci if not set
    outdir: null

    # memberOrgs will be used to label associated members as "internal"
    member_orgs:
      - llnl

    # all repos in these orgs are considered in your institution
    orgs:
     - cdat
     - llnl
     - mfem

    # Additional repos to add to the set (possibly not under an org above)
    repos:
     - alpine-dav/ascent
     - atomconsortium/ampl
     - ceed/benchmarks
 
    # do not include these repos in the assessment
    exclude_repos:
     - mfem/github-actions


This file should have the following fields:

.. list-table:: Title
   :widths: 25 65 10
   :header-rows: 1

   * - Name
     - Description
     - Default
     - Required
   * - member_orgs
     - A list of GitHub organizations that are core to your institution. If you are concerned about contibutions, everyone that is a member here is labeled as an internal contributor.
     - unset
     - yes
   * - orgs
     - A list of repos your organization members contribute to, but aren't necessarily owned by your institution.
     - unset
     - yes
   * - repos
     - A list of loose repos to add to the ones that are discovered under the orgs already provided.
     - unset
     - false
   * - exclude_repos
     - One or more repos to exclude given that they are found anywhere.
     - unset
     - false
   * - outdir
     - An output directory (must exist) to save results.
     - unset
     - $PWD/.cci


.. _getting_started-commands:


Commands
========

Once you have your configuration file, and exported a GitHub `personal access token <https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token>`_:

.. code-block:: console

    # Export a GitHub Personal Access Token
    $ export GITHUB_TOKEN=xxxxxxxxxxxxxx


...the following commands are available! For any command, you can specify a custom configuration file or output directory:

.. code-block:: console

    $ cci --config-file --out-dir <command> <args>


.. _getting_started-commands-extract:


List
----

You likely want to start with an extraction.
An extraction means that you are extracting metadata for the current data,
and for your current set of repos. But first you need to know what your
options are! For this purpose you can use ``list``:

.. code-block:: console

    $ cci list
               repos: contributor_ci.main.extractors.collection.repos.extract.Repos
               users: contributor_ci.main.extractors.collection.users.extract.Users


Extract
-------

You next likely want to run an extractor. The default output directory used
will be a directory named ``.cci`` for "contributor CI" in the present working
directory. 

.. code-block:: console

    $ cci extract repos
    Retrieving organization info for cdat
    Checking GitHub API token... Token validated.
    Auto-retry limit for requests set to 10.
    Reading '/home/vanessa/Desktop/Code/contributor-ci/contributor_ci/main/extractors/collection/repos/org-repos-info.gql' ... File read!
    Page 1
    Sending GraphQL query...
    Checking response...
    HTTP STATUS 200 OK

When it finished, you can inspect  the output in the present working directory
".cci" folder (unless you changed the path in the config or on the command line).
It is a tree organized by year, month, and day:

.. code-block:: console

     $ tree .cci/
     .cci/
     └── 2021
         └── 6
             └── 3
                 └── cci-repos.json
