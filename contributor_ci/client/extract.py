__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.logger import logger


def main(args, parser, extra, subparser):

    from contributor_ci.main import Client

    cli = Client(
        quiet=args.quiet,
        config_file=args.config_file,
        outdir=args.outdir,
        save_format=args.save_format,
    )

    # Allowed extractors
    available = list(cli.extractors) + ["all"]
    selected = args.method or []
    for extractor in selected:
        if extractor not in available:
            logger.exit(
                "%s is not a valid extraction method! Choose from %s."
                % (extractor, ",".join(available))
            )

    # Case 1: a request for ALL
    if "all" in selected:
        cli.extract_all()
    else:
        for method in selected:
            cli.extract(method)
