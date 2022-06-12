__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.logger import logger
from contributor_ci.main.extractor import GitHubExtractorBase


class RepoDependencies(GitHubExtractorBase):

    name = "repo_dependencies"
    description = "extract repository dependencies."
    filenames = ["repo_dependencies"]
    depends_on = ["repos"]

    def extract(self):
        """
        Extract repository dependencies.
        """
        dep_query = self.get_local_query("repo-dependencies.gql")

        # This extract only saves one result - a repos file
        self._data[self.name] = {}

        # We require internal repositories list as input
        repos = self.load_dependency_file("repos")
        repolist = sorted(repos.data.keys())
        logger.info("Found %s repositories to find dependencies for." % len(repolist))

        for i, repo in enumerate(repolist):
            logger.info(
                "Getting dependencies for %s, %s of %s" % (repo, i, len(repolist))
            )
            repo_user, repo_name = repo.split("/")
            try:
                out = self.manager.queryGitHubFromFile(
                    dep_query,
                    {
                        "ownName": repo_user,
                        "repoName": repo_name,
                        "numManifests": 100,
                        "numDependents": 100,
                        "pgCursor": None,
                    },
                    paginate=True,
                    cursorVar="pgCursor",
                    keysToList=[
                        "data",
                        "repository",
                        "dependencyGraphManifests",
                        "nodes",
                    ],
                    headers={"Accept": "application/vnd.github.hawkgirl-preview+json"},
                )
            except Exception as error:
                logger.warning("Warning: Could not complete '%s':%s" % (repo, error))
                continue

            # save dependency data for repository
            self._data[self.name][repo] = out["data"]["repository"]
