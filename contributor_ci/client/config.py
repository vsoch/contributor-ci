__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


import sys

from contributor_ci.logger import logger
from contributor_ci.main import Client


def main(args, parser, extra, subparser):

    cli = Client(quiet=args.quiet, config_file=args.config_file, outdir=args.outdir)

    # If nothing provided, show help
    if not args.params:
        print(subparser.format_help())
        sys.exit(0)

    # The first "param" is either sort, edit, set of get
    command = args.params.pop(0)

    # For each new setting, update and save!
    if command == "sort":
        cli.settings.sort()
        cli.settings.save()

    # Add is used for a list
    elif command in ["add", "remove"]:
        key = args.params.pop(0)
        if not cli.settings.get(key):
            logger.exit("The key %s must exist to add to it." % key)

        if not isinstance(cli.settings.get(key), list):
            logger.exit("You can only add a new entry to a list.")

        for param in args.params:
            if command == "add":
                cli.settings.add(key, param)
            else:
                cli.settings.remove(key, param)
        cli.settings.sort()
        cli.settings.save()

    # For each get request, print the param pair
    elif command == "edit":
        cli.settings.edit()
    else:
        logger.error("%s is not a recognized command." % command)
