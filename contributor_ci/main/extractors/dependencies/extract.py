__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.logger import logger
from contributor_ci.main.extractor import GitHubExtractorBase


class Dependencies(GitHubExtractorBase):

    name = "dependencies"
    description = "extract dependencies."
    filenames = ["dependencies"]
    depends_on = ["repo_dependencies"]

    def extract(self):
        """
        Extract more metadata about repository dependencies.
        """
        dep_query = self.get_local_query("dependencies-info.gql")

        # This extract only saves one result - a repos file
        self._data[self.name] = {}

        # We require internal repositories list as input
        depends = self.load_dependency_file("repo_dependencies")
        logger.info("Found %s dependencies to find metadata for." % len(depends.data))

        repolist = []
        # Generate a list (will have duplicates) of dependency names
        for i, name in enumerate(depends.data):
            for node in depends.data[name]["dependencyGraphManifests"]["nodes"]:
                for repo in node["dependencies"]["nodes"]:
                    if repo["repository"] and repo["repository"]["nameWithOwner"]:
                        repolist.append(repo["repository"]["nameWithOwner"])

        # This ensures unique!
        repolist = list(dict.fromkeys(repolist))
        repolist.sort()
        logger.info("Found %s dependency repositories." % len(repolist))
        for i, repo in enumerate(repolist):
            repo_user, repo_name = repo.split("/")
            logger.info(
                "Getting dependency metadata for %s, %s of %s"
                % (repo, i, len(repolist))
            )
            try:
                out = self.manager.queryGitHubFromFile(
                    dep_query,
                    {"ownName": repo_user, "repoName": repo_name},
                    headers={"Accept": "application/vnd.github.hawkgirl-preview+json"},
                )
            except Exception as error:
                logger.warning("Warning: Could not complete '%s': %s" % (repo, error))
                continue

            self._data[self.name][repo] = out["data"]["repository"]
