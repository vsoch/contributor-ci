__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.main.extractor import GitHubExtractorBase
from contributor_ci.logger import logger


class RepoMetadata(GitHubExtractorBase):

    name = "repo_metadata"
    description = "gather repository metadata from several extractors."
    depends_on = ["repos", "topics"]
    filenames = ["repo_metadata"]

    def extract(self):
        """
        Gather repository metadata from multiple extractors
        """
        self._data[self.name] = {}

        # Load in dependency files
        repos = self.load_dependency_file("repos")
        topics = self.load_dependency_file("topics")

        for repo in repos.data:
            logger.info("Combining metadata for repository %s" % repo)
            data = {}

            repository = repos.data[repo]
            data["name"] = repo
            data["description"] = repository["description"]
            data["website"] = repository["homepageUrl"]

            # Add topis
            if repository["repositoryTopics"]["totalCount"] > 0 and repo in topics.data:
                topic_repo = topics.data[repo]
                topiclist = []
                for topic in topic_repo["repositoryTopics"]["nodes"]:
                    topiclist.append(topic["topic"]["name"])
                data["topics"] = topiclist
            else:
                data["topics"] = None

            self._data[self.name][repo] = data
