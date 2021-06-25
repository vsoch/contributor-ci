__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.logger import logger
import os


def main(args, parser, extra, subparser):

    from contributor_ci.main import Client

    cli = Client(quiet=args.quiet, config_file=args.config_file, outdir=args.outdir)

    command = args.ui_command.pop(0)

    # By default, generate or update in PWD if nothing provided
    dirname = os.getcwd()
    if args.ui_command:
        dirname = args.ui_command.pop(0)

    if command == "generate":
        cli.ui_generate(dirname, include_cfa=args.include_cfa)

    elif command == "update":
        cli.ui_update(dirname)
    else:
        logger.exit("%s is not a known user interface command." % command)
