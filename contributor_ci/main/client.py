__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


from contributor_ci.logger import logger
import contributor_ci.utils as utils
from .settings import Settings
from .extractor import ExtractorFinder, ExtractorResolver

import os
import shutil
import sys


class Client:
    """
    Create a client to extract metrics and run Contributor CI.
    """

    def __init__(self, config_file=None, outdir=None, quiet=True):

        self.quiet = quiet
        self._outdir = outdir
        self.settings = Settings(config_file)
        self._extractors = None
        self._results = {}

    @property
    def out_dir(self):
        """
        Get the output directory for contributor ci results
        """
        if not hasattr(self, "_out_dir"):
            default = os.path.abspath(".cci")
            self._out_dir = self._outdir or self.settings.outdir or default
        return self._out_dir

    @property
    def extractors(self):
        """
        Get a list of extractirs available
        """
        if not self._extractors:
            self._finder = ExtractorFinder()
            self._extractors = dict(self._finder.items())
        return self._extractors

    def extract(self, method):
        """
        Extract metrics given a particular method
        """
        if method not in self.extractors:
            logger.exit("Extractor %s is not known." % method)

        ext = self.get_extractor(method)

        # Each extractor defines depends_on, and we need to create a DAG that
        # checks dependencies first (either running or finding that already run)
        lookup = {}
        resolver = ExtractorResolver()

        # Keep going until no more dependencies
        expanded = set([ext])
        seen = set()
        while expanded:
            ext = expanded.pop()
            lookup[ext.name] = ext
            if ext in seen:
                continue
            seen.add(ext)
            resolver.add_extractor(ext.name)
            for depname in ext.depends_on:
                dep = self.get_extractor(depname)
                resolver.add_extractor(dep.name)
                resolver.add_dependency(ext.name, dep.name)
                expanded.add(dep)

        order = resolver.resolve()

        ran = False
        for name in order:
            extractor = lookup[name]

            # Only run the extractor if the result does not exist
            if not extractor.exists():
                logger.info("## RUNNING %s extractor" % name)
                self._results[extractor.name] = extractor.extract()
                extractor.save_json()
                ran = True

        # No extractors to run?
        if not ran:
            logger.exit("Extractor runs are up to date.", return_code=0)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[contributor-ci-client]"

    def extract_all(self, versions=None):
        """
        Run all extractors
        """
        for name in self.extractors:
            self.extract(name)

    def get_extractor(self, name):
        """
        Load the extractor class based on its name and add settings.
        """
        ext = self._extractors[name]
        ext.settings = self.settings
        ext.outdir = self.out_dir
        return ext
