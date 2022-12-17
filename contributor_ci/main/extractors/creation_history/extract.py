__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

import re

from contributor_ci.logger import logger
from contributor_ci.main.extractor import GitHubExtractorBase


class CreationHistory(GitHubExtractorBase):

    name = "creation_history"
    description = "extract creation history for repositories."
    depends_on = ["repos"]
    filenames = ["creation_history"]

    def extract(self):
        """
        Extract metadata about creation history
        """
        self._data[self.name] = {}

        # Load in dependency files
        repos = self.load_dependency_file("repos")
        repolist = sorted(repos.data.keys())

        query_commits = "/repos/OWNNAME/REPONAME/commits?until=CREATETIME&per_page=100"
        query_commits_in = "/repos/OWNNAME/REPONAME/commits?per_page=100"

        # A recent dependency file is not a requirement
        history = self.load_recent_dependency_file("creation_history")
        if history:
            self._data[self.name] = history.data

        for i, repo in enumerate(repolist):
            logger.info(
                "Parsing creation history for repository %s, %s of %s"
                % (repo, i, len(repolist))
            )
            repo_user, repo_name = repo.split("/")

            # History doesn't change, only update new repos or those that had no previous commits
            if repo in self._data[self.name]:
                if self._data[self.name][repo].get("FirstCommitAt"):
                    logger.info("Already recorded data for '%s'" % (repo))
                    continue

            # Repository creation date
            repo_data = {"createdAt": repos.data[repo]["createdAt"]}

            # Commit timestamps
            gitquery2 = re.sub("OWNNAME", repo_user, query_commits)
            gitquery2 = re.sub("REPONAME", repo_name, gitquery2)
            gitquery2 = re.sub("CREATETIME", repo_data["createdAt"], gitquery2)

            try:
                out = self.manager.queryGitHub(gitquery2, rest=True, paginate=True)
            except Exception as error:
                out = []
                logger.warning("Could not complete '%s':%s" % (repo, error))

            # Update repo data
            repo_data["commitTimestamps"] = []
            self.update_commits(out, repo_data, repo)

            # If no pre-GitHub commits, check the greater commit history
            if repo_data["commitTimestamps"] and repo_data["commitTimestamps"][0]:
                repo_data["initBeforeGitHubRepo"] = True
            else:
                repo_data["initBeforeGitHubRepo"] = False

            gitquery3 = re.sub("OWNNAME", repo_user, query_commits_in)
            gitquery3 = re.sub("REPONAME", repo_name, gitquery3)

            try:
                out = self.manager.queryGitHub(gitquery3, rest=True, paginate=True)
            except Exception as error:
                print("Warning: Could not complete '%s': %s" % (repo, error))

            # Sort and save earlist commit date
            self.update_commits(out, repo_data, repo)
            repo_data["commitTimestamps"].sort()

            firstdate = None
            if repo_data["commitTimestamps"]:
                firstdate = repo_data["commitTimestamps"][0]
            repo_data["firstCommitAt"] = firstdate

            # We only need the first commit
            del repo_data["commitTimestamps"]

            self._data[self.name][repo] = repo_data

        # Clean up repos no longer in list
        updated = {}
        for repo in self._data[self.name]:
            if repo in repolist:
                updated[repo] = self._data[self.name][repo]

        self._data[self.name] = updated

    def update_commits(self, commits, repo_data, repo):
        """
        Update list of commit timestamps with new commit dates.
        """
        try:
            for commit in commits:
                repo_data["commitTimestamps"].append(
                    commit["commit"]["committer"]["date"]
                )
        except NameError:
            logger.info("Could not get pre-GitHub commits for '%s'" % (repo))
        return repo_data
