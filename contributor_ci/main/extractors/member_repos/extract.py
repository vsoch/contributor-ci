__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.logger import logger
from contributor_ci.main.extractor import GitHubExtractorBase


class MemberRepos(GitHubExtractorBase):

    name = "member_repos"
    description = "extract repositories that belong to members not within org."
    depends_on = ["users"]  # users already depends on repos
    filenames = ["member_repos"]

    def extract(self):
        """
        Extract metadata about member extra repositories.
        """
        self._data[self.name] = {}
        repo_query = self.get_local_query("user-repos.gql")

        # Load in dependency files
        repos = self.load_dependency_file("repos")
        users = self.load_dependency_file("internal-users")

        repolist = sorted(repos.data.keys())
        memberlist = sorted(users.data.keys())

        for user in memberlist:
            logger.info("Looking up extra repos for %s" % user)

            try:
                out = self.manager.queryGitHubFromFile(
                    repo_query,
                    {"userName": user, "numRepos": 50, "pgCursor": None},
                    paginate=True,
                    cursorVar="pgCursor",
                    keysToList=["data", "user", "repositoriesContributedTo", "nodes"],
                )
            except Exception as error:
                logger.warning("Warning: Could not complete '%s': %s" % (user, error))
                continue

            # Update collective data
            for repo in out["data"]["user"]["repositoriesContributedTo"]["nodes"]:
                key = repo["nameWithOwner"]

                # If the repository is an organization one, skip
                if key in repolist:
                    continue

                if key not in self._data[self.name]:
                    self._data[self.name][key] = repo
                self._data[self.name][key]["labContributors"] = {"nodes": []}
                self._data[self.name][key]["labContributors"]["nodes"].append(user)
                self._data[self.name][key]["labContributors"]["nodes"].sort()
