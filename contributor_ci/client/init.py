__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.main import Client
from contributor_ci.logger import logger


def main(args, parser, extra, subparser):

    client = Client(
        quiet=args.quiet,
        config_file=args.config_file,
        outdir=args.outdir,
        require_config=False,
    )

    if not args.username.startswith("user:") and not args.username.startswith("org:"):
        logger.exit("You must provide a user:<username> or org:<orgname>")
    client.init(args.username)
