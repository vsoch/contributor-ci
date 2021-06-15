__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.logger import logger


def main(args, parser, extra, subparser):

    from contributor_ci.main import Client

    # We require a config to generate for all
    require_config = False
    if args.repo == "all":
        require_config = True

    cli = Client(
        quiet=args.quiet,
        config_file=args.config_file,
        outdir=args.outdir,
        require_config=require_config,
    )
    markdown = cli.cfa(args.repo, save=not args.terminal)
    if args.terminal and args.repo == "all":
        logger.warning("Terminal print is not supported for multiple CFA assessments.")
    elif args.terminal:
        print(markdown)
