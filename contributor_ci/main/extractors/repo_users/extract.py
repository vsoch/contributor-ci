__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.logger import logger
from contributor_ci.main.extractor import GitHubExtractorBase


class RepoUsers(GitHubExtractorBase):

    name = "repo_users"
    description = "extract repositories worked on for external and internal users."
    depends_on = ["users"]  # users already depends on repos
    filenames = ["internal-users", "external-users"]

    def extract(self):
        """
        Extract metadata about internal and exernal users.
        """
        self._data["internal-repos"] = {}
        self._data["external-repos"] = {}

        repo_query = self.get_local_query("repo-users.gql")

        # Load in dependency files
        repos = self.load_dependency_file("repos")
        internal = self.load_dependency_file("internal-users")
        # external = self.load_dependency_file("external-users")

        repolist = sorted(repos.data.keys())
        memberlist = sorted(internal.data.keys())

        for repo in repolist:
            repo_user, repo_name = repo.split("/")

            try:
                out = self.manager.queryGitHubFromFile(
                    repo_query,
                    {
                        "ownName": repo_user,
                        "repoName": repo_name,
                        "numUsers": 50,
                        "pgCursor": None,
                    },
                    paginate=True,
                    cursorVar="pgCursor",
                    keysToList=["data", "repository", "mentionableUsers", "nodes"],
                )
            except Exception as error:
                logger.warning("Warning: Could not complete '%s': %s" % (repo, error))
                continue

            # Update collective data
            for user in out["data"]["repository"]["mentionableUsers"]["nodes"]:
                username = user["login"]
                if username in memberlist:
                    self.add_contributions(username, "internal-repos", repo)
                else:
                    self.add_contributions(username, "external-repos", repo)

    def add_contributions(self, username, key, repo):
        """
        Given a username and a key, add a repository node
        """
        if username not in self._data[key]:
            self._data[key][username] = {}
        if "contributedLabRepositories" not in self._data[key][username]:
            self._data[key][username]["contributedLabRepositories"] = {"nodes": []}
        self._data[key][username]["contributedLabRepositories"]["nodes"].append(repo)
        self._data[key][username]["contributedLabRepositories"]["nodes"].sort()
