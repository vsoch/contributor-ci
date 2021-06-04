__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


import contributor_ci.utils
from collections.abc import Mapping
from contributor_ci.logger import logger
from contributor_ci.main.settings import SettingsBase

from datetime import datetime

import abc
import os

here = os.path.abspath(os.path.dirname(__file__))


class ExtractorFinder(Mapping):
    """
    An ExtractorFinder keeps a cache of available extractors
    """

    _extractors = {}

    def __init__(self):
        """
        Instantiate an extractor
        """
        self.collection_path = os.path.join(here, "collection")
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
            lookup[name] = "contributor_ci.main.extractors.collection.%s.extract.%s" % (
                name,
                class_name,
            )
        return lookup


class ExtractorBase:

    name = "metric"
    description = "An abstract base extractor."
    date_time_format = "%Y-%m-%dT%H:%M:%S%z"

    def __init__(self, filename=__file__):

        # Empty settings to be replaced by loaded settings
        self.settings = SettingsBase()
        self._data = {}
        self.classpath = os.path.dirname(filename)

    @abc.abstractmethod
    def extract(self):
        """Run the extraction."""
        pass

    def require_github(self):
        """
        Require GitHub token in the environment
        """
        self.token = os.environ.get("GITHUB_TOKEN")
        if not self.token:
            logger.exit("GITHUB_TOKEN is required to use %s" % self.name)

    def get_results(self):
        return self._data

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

    def save_json(self, outdir):
        """
        Save results to json, organized by type and date.
        """
        results = self.get_results()

        # We want to organize output by date
        now = datetime.now()

        outdir = os.path.join(outdir, str(now.year), str(now.month), str(now.day))
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        for name, result in results.items():
            outfile = "cci-%s.json" % name
            outfile = os.path.join(outdir, outfile)
            contributor_ci.utils.write_json(result, outfile)
