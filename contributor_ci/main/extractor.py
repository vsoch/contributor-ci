__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


import contributor_ci.utils
from collections.abc import Mapping
from contributor_ci.logger import logger
from contributor_ci.main.settings import SettingsBase

from collections import defaultdict
from datetime import datetime

from scraper.github import queryManager as qm
import importlib

import inspect
import abc
import os

here = os.path.abspath(os.path.dirname(__file__))


class ExtractorFinder(Mapping):
    """
    An ExtractorFinder keeps a cache of available extractors
    """

    _extractors = {}

    def __init__(self, save_format=None):
        """
        Instantiate an extractor
        """
        self.save_format = save_format
        self.collection_path = os.path.join(here, "extractors")
        self.update()

    def __getitem__(self, name):
        return self._extractors.get(name)

    def __iter__(self):
        return iter(self._extractors)

    def __len__(self):
        return len(self._extractors)

    def update(self):
        """
        Update extractors
        """
        self._extractors = self._load_extractors()

    def _load_extractors(self):
        """
        Load extractors based on listing folders in the collection.
        """
        lookup = {}
        for name in os.listdir(self.collection_path):
            extractor_dir = os.path.join(self.collection_path, name)
            extractor_file = os.path.join(extractor_dir, "extract.py")

            # Skip files in collection folder
            if os.path.isfile(extractor_dir):
                continue

            # Continue if the file doesn't exist
            if not os.path.exists(extractor_file):
                logger.debug(
                    "%s does not appear to have an extract.py, skipping."
                    % extractor_dir
                )
                continue

            # The class name means we split by underscore, capitalize, and join
            class_name = "".join([x.capitalize() for x in name.split("_")])
            module = "contributor_ci.main.extractors.%s.extract" % name
            lookup[name] = getattr(importlib.import_module(module), class_name)(
                self.save_format
            )
        return lookup


class ExtractorBase:

    name = "metric"
    description = "An abstract base extractor."
    date_time_format = "%Y-%m-%dT%H:%M:%S%z"
    filenames = []
    depends_on = []

    def __init__(self, save_format=None):

        # Empty settings to be replaced by loaded settings
        self.settings = SettingsBase()
        self._data = {}
        self.save_format = save_format or "year/month/day"

        # If we change the output format, we cannot reliably date the output
        self.force_extract = self.save_format != "year/month/day"

        # This should be over-ridden typically by client get_extractor
        self.outdir = os.path.abspath(".cci")

    @abc.abstractmethod
    def extract(self):
        """Run the extraction."""
        pass

    @property
    def classpath(self):
        return os.path.dirname(inspect.getfile(self.__class__))

    def require_github(self):
        """
        Require GitHub token in the environment
        """
        self.token = os.environ.get("GITHUB_TOKEN")
        if not self.token:
            self.token = os.environ.get("CCI_GITHUB_TOKEN")
        if not self.token:
            logger.exit(
                "GITHUB_TOKEN or CCI_GITHUB_TOKEN is required to use %s" % self.name
            )

    def get_results(self):
        return self._data

    def exists(self):
        """
        Given output files known to the extactor, determine if already run.
        """
        outdir = self.get_dated_outdir()
        exists = True
        for name in self.filenames:
            outfile = "cci-%s.json" % name
            outfile = os.path.join(outdir, outfile)
            if os.path.exists(outfile) and self.force_extract:
                logger.debug(
                    "%s exists, but not reliably from today! Needs run." % outfile
                )
                exists = False
            elif not os.path.exists(outfile):
                logger.debug("%s does not exist, needs run." % outfile)
                exists = False
        return exists

    def get_dependency_file(self, name):
        """
        Given the name of a dependency file, retrieve it for the current data.
        """
        outdir = self.get_dated_outdir()
        filename = os.path.join(outdir, "cci-%s.json" % name)
        if not os.path.exists(filename):
            logger.exit("Dependency file %s does not exist." % filename)
        return filename

    def get_recent_dependency_file(self, name):
        """
        Given the name of a dependency file, find the latest.
        """
        filename = os.path.join(self.outdir, "data", "latest", "cci-%s.json" % name)
        if os.path.exists(filename):
            return filename

    def get_local_query(self, path):
        """
        Given the path of a graph ql (.gql) file in the collection, return it
        """
        path = os.path.join(self.classpath, path)
        if not os.path.exists(path):
            logger.exit(
                "Required GraphQL file %s does not exist alongside collection." % path
            )
        return path

    def get_dated_outdir(self):
        """
        Return nested directory name with year, month, day within data
        """
        outdir = self.outdir
        now = datetime.now()

        # Organize outdir by default year/month/day or custom
        outdir = os.path.join(outdir, "data")
        for level in self.save_format.split("/"):
            if level.lower() == "year":
                outdir = os.path.join(outdir, str(now.year))
            elif level.lower() == "month":
                outdir = os.path.join(outdir, str(now.month))
            elif level.lower() == "day":
                outdir = os.path.join(outdir, str(now.day))
        return outdir

    def save_json(self):
        """
        Save results to json, organized by type and date.
        """
        results = self.get_results()
        outdir = self.get_dated_outdir()

        # Also save as latest results
        latest = os.path.join(self.outdir, "data", "latest")

        for dirname in [latest, outdir]:
            if not os.path.exists(dirname):
                os.makedirs(dirname)

        for name, result in results.items():
            outname = "cci-%s.json" % name
            if result:
                for dirname in [outdir, latest]:
                    outfile = os.path.join(dirname, outname)
                    contributor_ci.utils.write_json(result, outfile)


class GitHubExtractorBase(ExtractorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Requires export of GITHUB_TOKEN
        self._manager = None

    def load_dependency_file(self, name):
        """
        Given the name of a dependency, find and load the file
        """
        filename = self.get_dependency_file(name)
        return qm.DataManager(filename, True)

    def load_recent_dependency_file(self, name):
        """
        Given the name of a dependency, find and load the file
        """
        filename = self.get_recent_dependency_file(name)
        if filename:
            return qm.DataManager(filename, True)

    @property
    def manager(self):
        """
        Get or initialize the GitHub GraphQL Manager
        """
        self.require_github()
        if not self._manager:
            # Create a query manager
            self._manager = qm.GitHubQueryManager(self.token)
        return self._manager


class ExtractorResolver:
    """
    Given an extractor, create a graph (DAG) to determine execution order.
    """

    def __init__(self):
        self.graph = defaultdict(list)  # dictionary containing adjacency List

    @property
    def vertices(self):
        return len(self.graph)

    def add_extractor(self, ext):
        """
        Add an extractor to the graph, regardless of dependencies
        """
        self.graph[ext] = []

    def add_dependency(self, ext, depends_on):
        """
        Add a dependency to the graph
        """
        self.graph[ext].append(depends_on)

    @property
    def keys(self):
        return list(self.graph)

    def order_helper(self, v, seen, result):
        """
        A helper function to order the dependencies
        """
        # Lookup key to the index
        key = self.keys[v]

        # The current index is visited
        seen[v] = True

        # Visit unvisited extractors
        for i, ikey in enumerate(self.graph[key]):
            if not seen[i]:
                self.order_helper(i, seen, result)

        result.append(key)

    def resolve(self):
        """
        Resolve dependencies
        """
        seen = [False] * self.vertices
        result = []

        for i in range(self.vertices):
            if not seen[i]:
                self.order_helper(i, seen, result)

        # Return reversed
        return result[::-1]
