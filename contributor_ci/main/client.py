__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


import os
import random

import contributor_ci.utils as utils
from contributor_ci.cfa import CFA
from contributor_ci.logger import logger
from contributor_ci.main.extractors.users import UserExtractor

from .extractor import ExtractorFinder, ExtractorResolver
from .settings import Settings, SettingsBase


class Client:
    """
    Create a client to extract metrics and run Contributor CI.
    """

    def __init__(
        self,
        config_file=None,
        outdir=None,
        quiet=True,
        require_config=True,
        save_format=None,
    ):
        self.quiet = quiet
        self._outdir = outdir
        self._extractors = None
        self.save_format = save_format
        self._results = {}
        self._init_settings(config_file, require_config)

    def _init_settings(self, config_file, require_config=True):
        """
        Init settings.
        """
        if require_config:
            self.settings = Settings(config_file)
        else:
            self.settings = SettingsBase()

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
        Get a list of extractors available
        """
        if not self._extractors:
            self._finder = ExtractorFinder(self.save_format)
            self._extractors = dict(self._finder.items())
        return self._extractors

    def init(self, username):
        """
        Create a new contributor-ci.yaml based on an org or username.
        """
        if not self.settings.config_file:
            self.settings.config_file = "contributor-ci.yaml"

        # If the config file specified already exists, no go
        if os.path.exists(self.settings.config_file):
            logger.exit(
                "%s already exists, remove to overwrite." % self.settings.config_file
            )
        result = UserExtractor().extract(username)
        # Validate and save the new config
        self.settings._settings = result
        self.settings.validate()
        self.settings.save(self.settings.config_file)

    def ui_generate(self, dirname, include_cfa=False):
        """
        Generate a new user interface.
        """
        dirname = os.path.abspath(dirname)

        # We've already checked for a config file!
        # If we already have a site here, no go
        for filename in ["_config.yml", "_layouts"]:
            if os.path.exists(os.path.join(dirname, filename)):
                logger.exit("A CCI site already exists here!")

        # Copy the entire contents of the site folder here
        site = os.path.join(utils.get_installdir(), "site")
        utils.copytree(site, dirname)
        self.ui_update(dirname, include_cfa=include_cfa)

    def ui_update(self, dirname, options=None, include_cfa=False):
        """
        Update an existing user interface.
        """
        options = options or {}
        dirname = os.path.abspath(dirname)

        # We've already checked for a config file!
        # If we already have a site here, no go
        for filename in ["_config.yml", "_layouts"]:
            if not os.path.exists(os.path.join(dirname, filename)):
                logger.exit("Missing CCI site. Run cci ui generate.")

        # Data is expected to be in cci
        self._out_dir = os.path.join(dirname, "cci")

        # Do we want to extract a random number?
        if "random" in options:
            self.extract_random(options["random"])
        else:
            self.extract_all()

        # CFA files will be here if they exist
        outdir = os.path.join(dirname, "_cfa")

        # Next, are we including CFA?
        if not os.path.exists(outdir):
            logger.info("%s has been updated." % dirname)
            return

        # Provide a different data directory
        if include_cfa:
            cfa = CFA(data_dir=self.out_dir)
            cfa.run_all(outdir)

    def cfa(self, repo, save=False):
        """
        Run the contributor friendliness assessment.

        A CFA assessment comes down to assessing a repository programatically
        for attributes of "contributor friendliness," either updating an
        existing markdown file with metadata or generating a new one if
        it does not exist.
        """
        cfa = CFA(data_dir=self.out_dir)

        # Save all to the cfa output directory, if don't exist
        outdir = os.path.join(self.out_dir, "cfa")
        if repo == "all" or save and not os.path.exists(outdir):
            os.makedirs(outdir)

        # If cfa is for all repos, we require a config
        if repo == "all":
            cfa.run_all(outdir)

        elif save:
            logger.info("Saving %s to %s" % (repo, outdir))
            return cfa.run(repo, save_to=outdir)

        else:
            return cfa.run(repo)

    def extract(self, method):
        """
        Extract metrics given a particular method. Given a particular save format,
        e.g., year/month/day ensure we save to that structure.
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
            logger.info("Extractor runs are up to date.")

    def extract_random(self, number):
        """
        Extract a random selection.
        """
        names = list(self.extractors.keys())
        for _ in range(number):

            # Cut out early if we run out!
            if not names:
                return
            choice = random.choice(names)
            names.pop(names.index(choice))
            self.extract(choice)

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
