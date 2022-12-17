__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

import re
from datetime import datetime

from contributor_ci.logger import logger
from contributor_ci.main.extractor import GitHubExtractorBase


class ActivityCommits(GitHubExtractorBase):

    name = "activity_commits"
    description = "extract internal repository commit activity."
    depends_on = ["repos"]
    filenames = ["activity_commits"]

    def extract(self):
        """
        Extract metadata about activity and commits
        """
        self._data[self.name] = {}

        # Load in dependency files
        repos = self.load_dependency_file("repos")
        repolist = sorted(repos.data.keys())

        query = "/repos/OWNNAME/REPONAME/stats/commit_activity"

        for repo in repolist:
            logger.info("Looking for commit history in %s" % repo)
            repo_user, repo_name = repo.split("/")
            gitquery = re.sub("OWNNAME", repo_user, query)
            gitquery = re.sub("REPONAME", repo_name, gitquery)

            try:
                out = self.manager.queryGitHub(gitquery, rest=True)
            except Exception as error:
                logger.warning("Warning: Could not complete '%s': %s" % (repo, error))
                continue

            for item in out:
                # We only want weekly totals
                if "days" in item:
                    del item["days"]

                # Convert unix timestamps into standard dates (rounded to nearest week)
                weekinfo = datetime.utcfromtimestamp(item["week"]).isocalendar()
                weekstring = str(weekinfo[0]) + "-W" + str(weekinfo[1]) + "-1"
                item["week"] = datetime.strptime(weekstring, "%Y-W%W-%w").strftime(
                    "%Y-%m-%d"
                )
                self._data[self.name][repo] = out
