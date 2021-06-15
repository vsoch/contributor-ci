.. _getting_started-user-guide:

==========
User Guide
==========

Contributor CI was created with the intention to help measure collaboration in
one or more repositories or an organization over time.
If you haven't read :ref:`getting_started-installation` you should do that first.


Quick Start
===========


.. code-block:: console

    # install contributor ci
    $ pip install contributor-ci

    # Export a GitHub Personal Access Token
    $ export GITHUB_TOKEN=xxxxxxxxxxxxxx

    # See metric extractors available
    $ cci list
    
    # Run an extraction
    $ cci extract repos

    # Generate a contributor friendliness assessment template
    $ cci cfa https://github.com/vsoch/salad
    

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
     - $PWD/.cci
     - true
   * - editor
     - An editor to use for cci config edit
     - vim
     - false

.. _getting_started-commands:


Commands
========

Once you have your configuration file, and exported a GitHub `personal access token <https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token>`_:

.. code-block:: console

    # Export a GitHub Personal Access Token
    $ export GITHUB_TOKEN=xxxxxxxxxxxxxx


...the following commands are available! For any command, you can specify a custom configuration file or output directory:

.. code-block:: console

    $ cci --config-file <config-file> --out-dir <out-dir> <command> <args>


.. _getting_started-commands-extract:


Config
------

Contributor CI provides an easy way to interact with your configuration file,
the file ``contributor-ci.yaml``. First, to edit the file, you can do:

.. code-block:: console

    $ cci config edit
    
By default, the editor chosen is vim. If you add an ``editor`` field
to that same file, you can choose an editor of your choice.
You can also quickly sort your file in the case that you made a bunch
of additions and want to ensure they are sorted. Note that sorting
happens automatically when you do an add or remove operation.

.. code-block:: console

    $ cci config sort


Next, you might want to add a repository or organization to a list. You can
use add and remove to do this. You should provide the key first (e.g. member_orgs)
followed by one more entries to add or remove.

.. code-block:: console

    $ cci config add member_orgs vsoch
    $ cci config remove member_orgs vsoch


List
----

You likely want to start with an extraction.
An extraction means that you are extracting metadata for the current data,
and for your current set of repos. But first you need to know what your
options are! For this purpose you can use ``list``:

.. code-block:: console

    $ cci list
        creation_history: extract creation history for repositories.
                  topics: extract repository topics.
       repo_dependencies: extract repository dependencies.
               languages: extract languages for a repository.
        activity_commits: extract internal repository commit activity.
                releases: extract repository releases.
                   stars: extract repository stars.
            member_repos: extract repositories that belong to members not within org.
          activity_lines: extract internal repository activity via lines of code.
            dependencies: extract dependencies.
           repo_metadata: gather repository metadata from several extractors. 
                   repos: extract repository metrics.
                   users: extract user metrics for a repository.
              repo_users: extract repositories worked on for external and internal users.


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
    .cci/data/
    └── 2021
        └── 6
            └── 13
                └── cci-repos.json

You'll notice that the extracted data is saved in a "data" subfolder.
This is because there are other output types that can be saved here.                 
                 

Extractors
==========

The following extractors are available.


.. list-table:: Contributor CI Extractors
   :widths: 25 65 10
   :header-rows: 1

   * - Name
     - Description
     - Depends On
   * - repos
     - Extract repository metadata
     - none
   * - users
     - Extract internal and external contributors lists
     - repos  
   * - repo_dependencies
     - Extract repository dependencies
     - repos
   * - dependencies
     - Extract dependency metadata
     - repo_dependencies
   * - releases
     - Extract releases for repositories
     - repos
   * - languages
     - Extract languages for repositories
     - repos
   * - activitycommits
     - Extract weekly number of repository commits to reflect activity
     - repos
   * - repo_users
     - Extract users and repositories contributed to (internal and external)
     - users    
   * - creation_history
     - Extract creation history (first commit) of repositories
     - repos
   * - stars
     - Extract repository stars
     - repos
   * - member_repos
     - Extract repositories of members not associated with the organization
     - users
   * - topics
     - Extract repository topics
     - repos
   * - repo_metadata
     - Combine repository metadata across repps and topics extractors
     - repos, topics


.. _getting_started-cfa:

Contributor Friendliness Assessment
===================================

The Contributor Friendliness Assessment (CFA) is an effort to identify
aspects of a repository that can be improved to make the repository more
contributor friendly. The assessment derives a list of criteria to assess how
easy it is to contribute to a project. This means arriving at a project
repository and having an easy time going from knowing nothing to opening a pull
request, and also how well the project attracts new contributors. Generally,
we assess the repository for:

 - ``CFA-branding``: Does the project have branding?
 - ``CFA-popularity``: How popular is the project?
 - ``CFA-description``: Does the project have a clear description (What is it for)?
 - ``CFA-need``: Does the project have a compelling set of use cases, or statement of need (Should I use it)? This is a fork in the visitor's decision tree, because if the answer is yes they will continue exploring, otherwise they will not.
 - ``CFA-license``: The GitHub repository has an OSI-approved open-source license.   
 - ``CFA-build``: Methods to build or install the software or service are clearly stated.
 - ``CFA-examples``: Does the README.md have a quick example of usage?
 - ``CFA-documentation``: Does the project have documentation?
 - ``CFA-support``: Does the project make it easy to ask for help?
 - ``CFA-developer``: Process and metadata is provided for the developer to understand and make changes.
 - ``CFA-quality``: The code quality of the project.
 - ``CFA-tests``: The project has testing.
 - ``CFA-coverage``: The project reports code coverage.
 - ``CFA-format``: The project adheres to a language specific format.
 - ``CFA-outreach``: Is the project active at conferences or otherwise externally presented?
 
Each of the items above has a more detailed description, rationale, and list
of criteria -- some of which are automated. Currently, the assessment
is under development so running the ``cfa`` tool for a repository:

.. code-block:: console

    # Generate a contributor friendliness assessment template and print to terminal
    $ cci cfa --terminal https://github.com/vsoch/salad

    # Save to local .cci directory
    $ cci cfa https://github.com/vsoch/salad

For the latter, your cfa template (with some fields populated) will be saved to 
your .cci output directory, as specified in your config or on the command line:

.. code-block:: console

    $ tree .cci/cfa/
    └── cfa-vsoch-salad.md


Will simply output the template to be filled in. This will be updated
with automation and allowing for save in the ``.cci`` output folder, allowing
for creating new assessments, and updating previously created assessments.
We will also provide a GitHub action for generating assessment files 
and opening a pull request when new repositories are found that have not
been assessed.

CFA Background
--------------

The author of CCI noticed that there are many good software projects, but
they don't do a good job of explaining use cases. She also noticed that small
details like branding, documentation, and ease of use were hugely important
variables for making it easy to contribute. You can imagine a sequence of
events (a decision tree) that models a user interaction:

1. Arrive at the repository.
2. Assess project for branding and popularity.
3. What does it do?
4. Does it help with a problem that I have?
  - yes --> continue
  - no  --> leave
5. Does it have a license that I like?
6. Install / build the software to try out
7. Look for a getting started guide or examples
8. Make changes to the repository, sometimes look for contributing guide.
9. Run local tests, formatting, etc.
10. Open a pull request


.. _getting_started-action:

GitHub Action
=============

Contributor CI comes with a GitHub action that will be more developed as the library
is developed. Currently, you can use it to run one or more extractors for
a ``repos.yaml`` in your repository. For example, let's say we want to
run all extractors:


.. code-block:: yaml

    name: Contributor CI Extract
    on: 
      schedule
    
        # Every Sunday
        - cron: 0 0 * * 0

    jobs:
      run:
        runs-on: ubuntu-latest
        steps:
        - name: Checkout Actions Repository
          uses: actions/checkout@v2
        - name: Extract
          uses: vsoch/contributor-ci@main
          env:
            CCI_GITHUB_TOKEN: ${{ secrets.CCI_GITHUB_TOKEN }}
          with: 
            extract: repos
            results_dir: .cci
            config_file: contributor-ci.yaml
        
        - name: Check that results exist
          run: tree .cci
    
        - name: Upload results
          if: success()
          uses: actions/upload-artifact@v2-preview
          with:
            name: cci-results
            path: .cci


Note that ``CCI_GITHUB_TOKEN`` is recommended to be a personal access token,
which is needed for some of the queries to look at organizations. If you just
need repository metadata, the standard ``GITHUB_TOKEN`` provided in actions
will suffice. You can either save as an artifact as shown above, or just push directly to a branch:


.. code-block:: yaml

  - name: Push Results
    run:
      git config --global user.name "github-actions"
      git config --global user.email "github-actions@users.noreply.github.com"
      git add _cci

      set +e
      git status | grep modified
      if [ $? -eq 0 ]; then
          set -e
          printf "Changes\n"
          git commit -m "Automated push with new data results $(date '+%Y-%m-%d')" || exit 0
          git push origin main
      else
        set -e
        printf "No changes\n"
      fi


You can also use `a pull request action <https://github.com/vsoch/pull-request-action>`_
to open a pull request instead. This action will be updated to better support generating
visualizations, etc.
