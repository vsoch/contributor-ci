__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

__version__ = "0.0.16"
AUTHOR = "Vanessa Sochat"
NAME = "contributor_ci"
AUTHOR_EMAIL = "vsoch@users.noreply.github.com"
PACKAGE_URL = "https://github.com/vsoch/contributor-ci"
KEYWORDS = "contributions, contributors, GitHub action, automated"
DESCRIPTION = "automated tools to assess contributions."
LICENSE = "LICENSE"

################################################################################
# Global requirements

INSTALL_REQUIRES = (
    ("Jinja2", {"min_version": None}),
    ("jsonschema", {"min_version": None}),
    ("ruamel.yaml", {"min_version": None}),
    ("llnl-scraper", {"min_version": "0.10.0"}),
)

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)

################################################################################
# Submodule Requirements (versions that include database)

INSTALL_REQUIRES_ALL = INSTALL_REQUIRES + TESTS_REQUIRES
