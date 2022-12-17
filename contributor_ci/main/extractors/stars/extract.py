__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from datetime import date, timedelta

from contributor_ci.logger import logger
from contributor_ci.main.extractor import GitHubExtractorBase


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + timedelta(days_ahead)


def toDate(isoStr):
    return next_weekday(date.fromisoformat(isoStr["starredAt"].split("T")[0]), 0)


class Stars(GitHubExtractorBase):

    name = "stars"
    description = "extract repository stars."
    depends_on = ["repos"]
    filenames = ["stars"]

    def extract(self):
        """
        Extract metadata about repository stars
        """
        self._data[self.name] = {}

        # Load in dependency files
        repos = self.load_dependency_file("repos")
        repolist = sorted(repos.data.keys())

        # load the query
        star_query = self.get_local_query("repo-stargazers.gql")

        for i, repo in enumerate(repolist):
            logger.info(
                "Parsing stargazer history for repository %s, %s of %s"
                % (repo, i, len(repolist))
            )
            repo_user, repo_name = repo.split("/")

            try:
                out = self.manager.queryGitHubFromFile(
                    star_query,
                    {
                        "ownName": repo_user,
                        "repoName": repo_name,
                        "numUsers": 100,
                        "pgCursor": None,
                    },
                    paginate=True,
                    cursorVar="pgCursor",
                    keysToList=["data", "repository", "stargazers", "edges"],
                )
            except Exception as error:
                logger.warning("Warning: Could not complete '%s': %s" % (repo, error))
                continue

            self._data[self.name][repo] = out["data"]["repository"]

        for repo in self._data[self.name]:
            dateRange = list(
                map(toDate, self._data[self.name][repo]["stargazers"]["edges"])
            )
            dateList = []
            dateElement = {"date": None, "value": None}
            for dateEntry in dateRange:
                if not dateElement["date"]:
                    dateElement["date"] = dateEntry.isoformat()
                    dateElement["value"] = 1
                elif dateElement["date"] == dateEntry.isoformat():
                    dateElement["value"] += 1
                else:
                    dateList.append(dateElement.copy())
                    dateElement["date"] = dateEntry.isoformat()
                    dateElement["value"] = 1
            self._data[self.name][repo] = dateList
