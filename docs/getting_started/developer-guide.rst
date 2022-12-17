.. _getting_started-developer-guide:

===============
Developer Guide
===============

This developer guide includes instructions for how to write an extractor.
If you haven't read :ref:`getting_started-installation` you should do that first.


Writing an Extractor
====================

An extractor is a directory in the folder ``contributor_ci/main/extractors``.
The directory should correspond to the name of the extractor (e.g., users or repos)
and within should minimally be an ``extract.py`` file.


Extractor Base Classes
----------------------

You can use an extractor base class to get access to all the functions to
save, load, and otherwise run an extraction. Specifically, if you are using
a GitHub extractor, you can import the ``GitHubExtractorBase``:

.. code-block:: console

    from contributor_ci.main.extractor import GitHubExtractorBase

If you don't require GitHub and are extracting metadata in some other way,
the ``ExtractorBase`` should be sufficient.


.. code-block:: console

    from contributor_ci.main.extractor import ExtractorBase

GitHub Extractor Base
^^^^^^^^^^^^^^^^^^^^^

The ``GitHubExtractorBase`` required a ``GITHUB_TOKEN`` to be exported in the
environment, and comes with a ``self.manager`` that is a query manager from
`this scraper tool <https://github.com/LLNL/scraper>`_. This tool uses graphQL queries
that should be located in the same directory as the extractor. For example,
the users extractor has several query files (extension *.gql) as you can see here:

.. code-block:: console

    $ tree contributor_ci/main/extractors/users/
    contributor_ci/main/extractors/users/
    ├── extract.py
    ├── __init__.py
    ├── org-members.gql
    └── repo-users.gql


There are several helper functions to support loading files, and reading any
previously extracted dependency files. As long as you add ``depends_on`` to your
extractor, there is an ``ExtractorResolver`` class that will make sure your dependency
data is produced before the extractor is run. You can do any of the following:

.. code-block:: console

    # Load the dependency file named cci-repos.json
    # repos.data will have the loaded data
    repos = self.load_dependency_file("repos")

    # Load the query filename org-repos-info.gql in the extractor directory
    org_query = self.get_local_query("org-repos-info.gql")


For running queries, it's recommended that you look at already existing
GitHub extractors for examples.


Extractor Metadata
------------------

Each extractor is required to have a set of properties that help to identify it.
Specifically:


.. list-table:: Title
   :widths: 25 65 10
   :header-rows: 1

   * - Name
     - Description
     - Required
   * - name
     - The extractor name, which should match the folder it lives in.
     - true
   * - description
     - A description of the extractor.
     - true
   * - filenames
     - The filename identifiers that the extractor is expected to save. E.g., if the "repos" extractor saves a file called "cci-repos.json", you would provide a list with "repos."
     - true
   * - depends_on
     - A list of other extractor names that this extractor depends on
     - false


You will also want to name your extractor the same as the directory and name,
but uppercase. This is how the class is discovered. As an example, here is the "users" extractor.

.. code-block:: python

    class Users(GitHubExtractorBase):

        name = "users"
        description = "extract user metrics for a repository."
        depends_on = ["repos"]
        filenames = ["internal-users", "external-users"]


This extractor requires that the "repos" extractor is run first (the depends_on field)
because we need a list of organization repositories to find members in.
This means that if someone runs:

.. code-block:: console

    cci extract users

The "repos" extractor will be run first as the dependency. You'll also notice
that filenames include "internal-users" and "external-users," and these will
generate output files in the nested output directory named accordingly. After
running this extractor, you'll see:

.. code-block:: console

    $ tree .cci/
    .cci/
    └── 2021
        └── 6
            ├── 3
            │   └── cci-repos.json
            └── 5
                ├── cci-external-users.json
                ├── cci-internal-users.json
                └── cci-repos.json

    4 directories, 4 files


Extractor Functions
-------------------

Your extractor is required to have one main function called ``extract`` to
do whatever extraction is needed and save results to ``self._data``.
Importantly, the keys to ``self._data`` should correspond with the file key
you intend to save. For the repos extractor, this means we save data to
``self._data["repos"]``` or just ``self._data[self.name]`` and for the
users extractor we expect to find data keys "internal-users" and "external-users."
That's it! As long as you have a function to extract, provide the necessary metadata,
and populate the data into ``self._data`` correctly, you should be good to go.
