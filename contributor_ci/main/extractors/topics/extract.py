__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.main.extractor import GitHubExtractorBase
from contributor_ci.logger import logger


class Topics(GitHubExtractorBase):

    name = "topics"
    description = "extract repository topics."
    depends_on = ["repos"]
    filenames = ["topics"]

    def extract(self):
        """
        Extract metadata about repository topics.
        """
        self._data[self.name] = {}
        topics_query = self.get_local_query("repo-topics.gql")

        # Load in dependency files
        repos = self.load_dependency_file("repos")

        repolist = sorted(repos.data.keys())

        for repo in repolist:
            logger.info("Looking up topics for %s" % repo)
            repo_user, repo_name = repo.split("/")

            try:
                out = self.manager.queryGitHubFromFile(
                    topics_query,
                    {
                        "ownName": repo_user,
                        "repoName": repo_name,
                        "numTopics": 25,
                        "pgCursor": None,
                    },
                    paginate=True,
                    cursorVar="pgCursor",
                    keysToList=["data", "repository", "repositoryTopics", "nodes"],
                )
            except Exception as error:
                logger.warning("Warning: Could not complete '%s': %s" % (repo, error))
                continue

            self._data[self.name][repo] = out["data"]["repository"]
