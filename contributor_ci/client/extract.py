__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.logger import logger


def main(args, parser, extra, subparser):

    from contributor_ci.main import Client

    cli = Client(quiet=args.quiet, config_file=args.config_file, outdir=args.outdir)

    # Allowed extractors
    available = list(cli.extractors) + ["all"]
    if args.method not in available:
        logger.exit(
            "%s is not a valid extraction method! Choose from %s." % ",".join(available)
        )

    if args.method == "all":
        cli.extract_all()
    else:
        cli.extract(args.method)
