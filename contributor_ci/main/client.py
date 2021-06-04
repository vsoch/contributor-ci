__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


from contributor_ci.logger import logger
import contributor_ci.utils as utils
from .settings import Settings
from .extractors.base import ExtractorFinder

import importlib
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
        _, extractor_name = self._extractors[method].rsplit(".", 1)
        self._results[extractor_name] = ext.extract()
        ext.save_json(self.out_dir)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[contributor-ci-client]"

    def extract_all(self, versions=None):
        print("EXTRACT ALL")
        import IPython

        IPython.embed()
        for name in self.extractors:
            self.extract(name)

    def get_extractor(self, name):
        """
        Load the extractor class based on its name and add settings.
        """
        module, extractor_name = self._extractors[name].rsplit(".", 1)
        ext = getattr(importlib.import_module(module), extractor_name)()
        ext.settings = self.settings
        return ext
