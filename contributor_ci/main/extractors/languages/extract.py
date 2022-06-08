__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.main.extractor import GitHubExtractorBase
from contributor_ci.logger import logger


class Languages(GitHubExtractorBase):

    name = "languages"
    description = "extract languages for a repository."
    depends_on = ["repos"]
    filenames = ["languages"]

    def extract(self):
        """
        Extract metadata about repository languages.
        """
        self._data[self.name] = {}
        lang_query = self.get_local_query("repo-languages.gql")
        repos = self.load_dependency_file("repos")

        # Prepare repository names
        repolist = sorted(repos.data.keys())
        logger.info("Found %s associated repos parsed today." % len(repolist))
        for repo in repolist:
            logger.info("Looking up languages for %s" % repo)
            repo_user, repo_name = repo.split("/")

            try:
                out = self.manager.queryGitHubFromFile(
                    lang_query,
                    {
                        "ownName": repo_user,
                        "repoName": repo_name,
                        "numLangs": 25,
                        "pgCursor": None,
                    },
                    paginate=True,
                    cursorVar="pgCursor",
                    keysToList=["data", "repository", "languages", "nodes"],
                )
            except Exception as error:
                logger.warning("Warning: Could not complete '%s': %s" % (repo, error))
                continue

            self._data[self.name][repo] = out["data"]["repository"]
