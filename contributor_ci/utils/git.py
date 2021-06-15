__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

import os
import re
from .terminal import run_command
from contributor_ci.logger import logger


class GitManager:
    """
    Interact with a Git repository.
    """

    def __init__(self, folder=None, quiet=False):
        """
        Initialize a git manager.

        The folder can be empty if intending to
        init a new repository, or not existing if a clone is intended.
        """
        self.folder = folder or ""
        self.quiet = quiet
        self.repo = None
        self.update_repo(self.folder)

    def update_repo(self, dest):
        self.git_dir = os.path.join(dest, ".git")
        if os.path.exists(self.git_dir):
            self.repo = dest
            self.folder = dest

    @property
    def reponame(self):
        """
        Get the respository name.
        """
        if self.repo:
            name = self.run_command(
                self.init_cmd(self.repo) + ["config", "--get", "remote.origin.url"]
            ).strip()
            return (
                re.sub("http://|https://|[.]git|github.com|git@", "", name)
                .strip("/")
                .strip(":")
            )

    @property
    def reponame_flat(self):
        return self.reponame.replace("/", "-")

    def add(self, filename=".", dest=None):
        """
        Add a file to the git repository
        """
        dest = dest or self.folder or ""
        return self.run_command(self.init_cmd(dest) + ["add", filename])

    def commit(self, message, dest=None):
        """
        Commit to a particular directory
        """
        dest = dest or self.folder or ""
        return self.run_command(
            self.init_cmd(dest)
            + [
                "-c",
                "commit.gpgsign=false",
                "commit",
                "-a",
                "-m",
                message,
                "--allow-empty",
            ]
        )

    def status(self, dest=None):
        """
        Add a file to the git repository
        """
        dest = dest or self.folder or ""
        return self.run_command(self.init_cmd(dest) + ["status"])

    def clone(self, repo, dest=None):
        """
        Given a repository, clone it with run_command
        """
        # Destination folder can default to present working directory
        dest = dest or self.folder or ""
        self.run_command(["git", "clone", "--depth", "1", repo, dest])

        # Disable warnings about detached head
        self.config("advice.detachedHead", "false", dest)
        self.update_repo(dest)
        return dest

    def init(self, dest=None):
        """
        Init an empty repository in a directory of choice
        """
        dest = dest or self.folder or ""
        self.run_command(["git", "init", dest])
        self.update_repo(dest)
        self.config("user.name", "contributor-ci", dest)
        self.config("user.email", "contributor-ci@users.noreply.github.com", dest)
        return dest

    def config(self, key, value, dest=None):
        self.run_command(self.init_cmd(dest) + ["config", key, value])

    def checkout(self, commit, dest=None):
        self.run_command(self.init_cmd(dest) + ["checkout", commit])

    def ls_files(self, dest=None):
        """
        Init an empty repository in a directory of choice
        """
        dest = dest or self.folder or ""
        files = self.run_command(self.init_cmd(dest) + ["ls-files"]) or []
        if files:
            return [x for x in files[0].split("\n") if x]
        return files

    def tag(self, tag, dest=None):
        """
        Create a tag for a particular commit
        """
        dest = dest or self.folder or ""
        return self.run_command(self.init_cmd(dest) + ["tag", tag])

    def init_cmd(self, dest):
        """
        Initialize a command that sets the git-dir and working tree
        """
        dest = dest or "."
        git_dir = os.path.join(dest, ".git")
        return [
            "git",
            "--git-dir=%s" % git_dir,
            "--work-tree=%s" % os.path.dirname(git_dir),
        ]

    def run_command(self, cmd):
        """
        A wrapper to run_command to handle errors
        """
        logger.debug(" ".join(cmd))
        response = run_command(cmd)
        if not response["return_code"] == 0:
            logger.exit("Error with %s, %s" % (" ".join(cmd), response["message"]))
        return response["message"]
