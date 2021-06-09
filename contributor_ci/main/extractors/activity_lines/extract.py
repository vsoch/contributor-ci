__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.main.extractor import GitHubExtractorBase
from contributor_ci.logger import logger
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ActivityLines(GitHubExtractorBase):

    name = "activity_lines"
    description = "extract internal repository activity via lines of code."
    depends_on = ["repos"]
    filenames = ["activity_lines"]

    def extract(self):
        """
        Extract metadata about lines of code.
        """
        self._data[self.name] = {}

        # Load in dependency files
        repos = self.load_dependency_file("repos")
        repolist = sorted(repos.data.keys())

        # Code frequency endpoint
        query_in = "/repos/OWNNAME/REPONAME/stats/code_frequency"

        # Cutoff timestamp
        cutoff = int((datetime.now() - relativedelta(years=1)).timestamp())

        for repo in repolist:
            logger.info("Looking for lines of code in %s" % repo)
            repo_user, repo_name = repo.split("/")

            gitquery = re.sub("OWNNAME", repo_user, query_in)
            gitquery = re.sub("REPONAME", repo_name, gitquery)

            try:
                out = self.manager.queryGitHub(gitquery, rest=True)
            except Exception as error:
                logger.warning("Warning: Could not complete '%s': %s" % (repo, error))
                continue

            # Limit data to the past year
            out = list(filter(lambda x: x[0] > cutoff, out))

            for item in out:
                # Convert unix timestamps into standard dates (rounded to nearest week)
                weekinfo = datetime.utcfromtimestamp(item[0]).isocalendar()
                weekstring = str(weekinfo[0]) + "-W" + str(weekinfo[1]) + "-1"
                item[0] = datetime.strptime(weekstring, "%Y-W%W-%w").strftime(
                    "%Y-%m-%d"
                )

            self._data[self.name][repo] = out
