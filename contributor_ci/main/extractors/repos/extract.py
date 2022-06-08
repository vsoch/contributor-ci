__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.logger import logger
from contributor_ci.main.extractor import GitHubExtractorBase


class RepoExtractor(GitHubExtractorBase):
    """
    A separate extractor used by the CFA to get metadata for one repository.
    """

    def extract(self, repo=None, reuse=False):

        repo_owner, repo_name = repo.split("/")

        # Can we re-use an older result?
        if reuse:
            repos = self.load_recent_dependency_file("repos")
            if repos is not None and repo in repos.data:
                return repos.data[repo]

        repo_query = self.get_local_query("repos-info.gql")
        logger.info("\nRetrieving repository info for %s" % repo)
        try:
            out = self.manager.queryGitHubFromFile(
                repo_query, {"ownName": repo_owner, "repoName": repo_name}
            )
        except Exception as error:
            logger.exit("Warning: Could not complete '%s'\n%s" % (repo, error))

        return out["data"]["repository"]


class Repos(GitHubExtractorBase):

    name = "repos"
    description = "extract repository metrics."
    filenames = ["repos"]

    def extract(self):
        """
        Extract repository metadata for orgs and repos.
        """
        self.extract_orgs()
        self.extract_repos()

    def extract_orgs(self):
        """
        Extract list of orgs from the contributor-ci.yaml and update data.
        """
        org_query = self.get_local_query("org-repos-info.gql")

        # This extract only saves one result - a repos file
        self._data[self.name] = {}

        # Exclude these repos
        excludes = self.settings.exclude_repos if self.settings.exclude_repos else []

        # This is going to retrieve repo-level data across the orgs
        for org in self.settings.orgs:
            logger.info("\nRetrieving organization info for %s" % org)

            try:
                out = self.manager.queryGitHubFromFile(
                    org_query,
                    {"orgName": org, "numRepos": 50, "pgCursor": None},
                    paginate=True,
                    cursorVar="pgCursor",
                    keysToList=["data", "organization", "repositories", "nodes"],
                )
            except Exception as error:
                logger.warning("Warning: Could not complete '%s'\n%s" % (org, error))
                continue

            # Add repositories from organization to our data
            for repo in out["data"]["organization"]["repositories"]["nodes"]:

                # Do not add repos that are explicitly excluded!
                if repo["nameWithOwner"] not in excludes:
                    self._data[self.name][repo["nameWithOwner"]] = repo

    def extract_repos(self):
        """
        Add metadata for additional isolated repos in the contibutor-ci.yaml
        """
        repo_query = self.get_local_query("repos-info.gql")

        # Add additional individual repos
        for repo in self.settings.repos:

            # Did we already extract it via an organization?
            if repo in self._data[self.name] or (
                self.settings.exclude_repos and repo in self.settings.exclude_repos
            ):
                continue
            logger.info("\nRetrieving repository info for %s" % repo)
            repo_owner, repo_name = repo.split("/")
            try:
                out = self.manager.queryGitHubFromFile(
                    repo_query, {"ownName": repo_owner, "repoName": repo_name}
                )
            except Exception as error:
                logger.warning("Warning: Could not complete '%s'\n%s" % (repo, error))
                continue

            key = out["data"]["repository"]["nameWithOwner"]
            self._data[self.name][key] = out["data"]["repository"]


class ReposExtractor(Repos):
    """
    A separate extractor used by the CFA to get metadata for all repos
    """

    def extract(self, reuse=False):

        # Can we re-use an older result?
        if reuse:
            repos = self.load_recent_dependency_file("repos")
            if repos is not None:
                return repos.data

        self.extract_orgs()
        self.extract_repos()
        return self._data
