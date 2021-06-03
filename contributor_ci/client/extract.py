__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.logger import logger


def main(args, parser, extra, subparser):

    from contributor_ci.main import Client

    cli = Client(quiet=args.quiet, config_file=args.config_file, outdir=args.outdir)

    # Allowed extractors
    if args.method not in ["users", "repos", "all"]:
        logger.exit(
            "%s is not a valid extraction method! Choose from %s."
            % ",".join(cli.extractors)
        )

    cli.extract(args.method)
