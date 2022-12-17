__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.logger import logger
from contributor_ci.main.extractor import GitHubExtractorBase


class UserExtractor(GitHubExtractorBase):
    """
    A separate extractor used by CCI init to get metadata for one user or org
    """

    def extract(self, username):

        # username is provided as user:<username> or org:orgname
        usertype, username = username.split(":", 1)
        config = {"member_orgs": None, "orgs": set(), "repos": set()}

        # If no username provided, we use running user account:
        if usertype == "user":
            user_query = self.get_local_query("user-info.gql")

            out = self.manager.queryGitHubFromFile(
                user_query,
                {"numRepos": 100, "pgCursor": None},
                paginate=True,
                cursorVar="pgCursor",
                keysToList=["data", "viewer", "repositories", "nodes"],
            )

            for node in out["data"]["viewer"]["repositories"]["nodes"]:

                # skip private repos
                if node["isPrivate"]:
                    continue

                if node["owner"]["login"] == username:
                    config["repos"].add("%s/%s" % (username, node["name"]))
                else:
                    config["orgs"].add(node["owner"]["login"])

        elif usertype == "org":
            config["member_orgs"] = [username]
            config["orgs"].add(username)
        else:
            logger.exit(
                "%s is not a valid extraction type. Please specify user:<username> or org:<orgname>"
            )

        config["orgs"] = list(config["orgs"])
        config["repos"] = list(config["repos"])
        return config


class Users(GitHubExtractorBase):

    name = "users"
    description = "extract user metrics for a repository."
    depends_on = ["repos"]
    filenames = ["internal-users", "external-users"]

    def extract(self):
        """
        Extract metadata about internal and exernal users.
        """
        self.extract_internal_users()
        self.extract_external_users()

    def extract_internal_users(self):
        """
        Extract internal users from member orgs
        """
        self._data["internal-users"] = {}
        org_query = self.get_local_query("org-members.gql")

        # Retrieve members from member orgs.
        for org in self.settings.member_orgs:
            logger.info("\nRetrieving organization members for '%s'" % org)

            try:
                out = self.manager.queryGitHubFromFile(
                    org_query,
                    {"orgName": org, "numUsers": 50, "pgCursor": None},
                    paginate=True,
                    cursorVar="pgCursor",
                    keysToList=["data", "organization", "membersWithRole", "nodes"],
                )
            except Exception as error:
                print("Warning: Could not complete '%s': %s" % (org, error))
                continue

            # Update collective data
            for user in out["data"]["organization"]["membersWithRole"]["nodes"]:
                self._data["internal-users"][user["login"]] = user

    def extract_external_users(self):
        """
        Find contributors across repos to label as external
        """
        users_query = self.get_local_query("repo-users.gql")

        # We will save internal and external users to file
        self._data["external-users"] = {}
        repos = self.load_dependency_file("repos")

        # Prepare repository names
        repolist = sorted(repos.data.keys())
        logger.info("Found %s associated repos parsed today." % len(repolist))

        # We need to already have the internal users
        if "internal-users" not in self._data:
            self.extract_internal_users()
        memberlist = sorted(self._data["internal-users"].keys())

        # Find contributors not associated with the org
        for repo in repolist:
            logger.info("Looking for contributors in %s" % repo)
            repo_user, repo_name = repo.split("/")

            try:
                out = self.manager.queryGitHubFromFile(
                    users_query,
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
                print("Warning: Could not complete '%s': %s" % (repo, error))
                continue

            # The users are found here!
            for user in out["data"]["repository"]["mentionableUsers"]["nodes"]:
                if user["login"] in memberlist:
                    self.update_internal_user(user, repo)
                else:
                    self.update_external_user(user, repo)

    def update_internal_user(self, user, repo):
        return self._update_user_metadata(user, repo, "internal-users")

    def update_external_user(self, user, repo):
        return self._update_user_metadata(user, repo, "external-users")

    def _update_user_metadata(self, user, repo, key):
        """
        Given a username and a repository, update the data to include it.
        """
        username = user["login"]

        # External users will not be in list yet
        if username not in self._data[key]:
            self._data[key][username] = user

        if "contributedLabRepositories" not in self._data[key][username]:
            self._data[key][username]["contributedLabRepositories"] = {"nodes": []}
        self._data[key][username]["contributedLabRepositories"]["nodes"].append(repo)
        self._data[key][username]["contributedLabRepositories"]["nodes"].sort()
