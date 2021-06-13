__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


from contributor_ci.logger import logger
import contributor_ci.utils as utils
from jinja2 import Template

import os
import shutil
import sys

here = os.path.abspath(os.path.dirname(__file__))


class CFA:
    """
    Create a client to assess contributor friendliness
    """

    def __init__(self, repo, template=None):
        self.repo = repo
        self.config = utils.read_yaml(os.path.join(here, "cfa.yaml"))
        self.template = template or os.path.join(here, "template.md")

    def __repr__(self):
        return str(self)

    def run(self):
        """Main function to run an entire contributor friendliness assessment"""
        # Determine if we have a path or repository
        if os.path.exists(os.path.abspath(self.repo)):
            repo = os.path.abspath(self.repo)

        # Assume we have git repository to clone
        elif self.repo.startswith("http"):
            repo = utils.clone(self.repo)

        # TODO: we will run some automated criteria extraction here
        return Template(utils.read_file(self.template)).render(
            items=self.config, repository=repo
        )

    def __str__(self):
        return "[contributor-friendliness-assesser]"
