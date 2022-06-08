__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


from contributor_ci.logger import logger
from contributor_ci.main.extractors.repos import RepoExtractor, ReposExtractor
import contributor_ci.utils as utils
from jinja2 import Template

from copy import deepcopy
import os
import shutil

here = os.path.abspath(os.path.dirname(__file__))


class CFA:
    """
    Create a client to assess contributor friendliness
    """

    def __init__(self, template=None, data_dir=None):
        self.config = utils.read_yaml(os.path.join(here, "cfa.yaml"))
        self.template = template or os.path.join(here, "template.md")
        self.data_dir = data_dir
        self._cache = {}

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[contributor-friendliness-assesser]"

    def run(self, repo, save_to=None):
        """
        Run an entire contributor friendliness assessment for a repository
        """
        git = utils.GitManager()

        # Determine if we have a path or repository
        if os.path.exists(os.path.abspath(repo)):
            git.update_repo(os.path.abspath(repo))

        # Assume we have git repository to clone
        elif repo.startswith("http"):
            git.clone(repo, dest=utils.get_tmpdir())

        # Cut out early if the file exists
        if save_to:
            outfile = os.path.join(save_to, "cfa-%s.md" % git.reponame_flat)
            if os.path.exists(outfile):
                return utils.read_file(outfile)

        # Generate results
        logger.info("Generating CFA for %s" % repo)
        result = self.extract_criteria(git)
        rendered = Template(utils.read_file(self.template)).render(
            items=result, repository=git.reponame
        )

        # If we want to save to file
        if save_to:
            if not os.path.exists(save_to):
                os.makedirs(save_to)
            utils.write_file(outfile, rendered)

        # Clean up
        if os.path.exists(git.folder):
            shutil.rmtree(git.folder)

        return rendered

    def run_all(self, save_to):
        """
        Run a contributor friendliness assessment for all repos known.

        Save to (outdir) is required here.
        """
        repos = self.get_cached_result("repos", ReposExtractor)
        for repo in repos:
            self.run("https://github.com/%s" % repo, save_to)

    def get_cached_result(self, name, Extractor, key=None):
        """
        Get a cached result - useful for metrics that use common data.
        """
        # Return cached result if already exists
        if name in self._cache:
            return self._cache[name]

        extractor = Extractor()
        if self.data_dir:
            extractor.outdir = self.data_dir

        # Otherwise, generate the data
        if key:
            meta = extractor.extract(key, reuse=True)
        else:
            meta = extractor.extract(reuse=True)

        # Save new result to cache and return
        self._cache[name] = meta
        return meta

    def extract_criteria(self, repo):
        """
        Given a repository, run methods to extract criteria details
        """
        result = deepcopy(self.config)

        # Run any functions defined in the config
        for key, content in result.items():
            for crit in content.get("criteria", {}):
                if "method" in crit:
                    func = getattr(self, crit["method"], None)
                    if func:
                        metric = func(repo)
                        if metric:
                            crit["result"] = metric
                        if metric and crit.get("type") == "boolean":
                            crit["met"] = True
                    else:
                        logger.warning("CFA does not have method %s" % crit["method"])

        return result

    def count_stars(self, repo):
        meta = self.get_cached_result("repo", RepoExtractor, repo.reponame)
        return meta["stargazers"]["totalCount"]

    def count_forks(self, repo):
        meta = self.get_cached_result("repo", RepoExtractor, repo.reponame)
        return meta["forks"]["totalCount"]

    def get_description(self, repo):
        meta = self.get_cached_result("repo", RepoExtractor, repo.reponame)
        return meta.get("description")

    def has_license(self, repo):
        meta = self.get_cached_result("repo", RepoExtractor, repo.reponame)
        license = meta.get("licenseInfo", {})
        if license:
            return license.get("spdxId") is not None

    def get_license_type(self, repo):
        meta = self.get_cached_result("repo", RepoExtractor, repo.reponame)
        license = meta.get("licenseInfo", {})
        if license:
            return license.get("spdxId")

    def get_build_framework(self, repo):
        pass

    def get_url(self, repo):
        meta = self.get_cached_result("repo", RepoExtractor, repo.reponame)
        return meta.get("homepageUrl")
