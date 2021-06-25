__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.logger import logger
import random
import os


def parse_option(options, option):
    """
    Parse an option into a name and value
    """
    # Currently supported options
    if not option.startswith("random"):
        logger.exit("%s is not a supported option." % option)
    if ":" in option:
        name, value = option.split(":", 1)
    else:
        name = option
        value = random.choice(range(2, 4))
    options[name] = int(value)
    return options


def main(args, parser, extra, subparser):

    from contributor_ci.main import Client

    cli = Client(quiet=args.quiet, config_file=args.config_file, outdir=args.outdir)

    command = args.ui_command.pop(0)

    # By default, generate or update in PWD if nothing provided
    dirname = os.getcwd()

    # We only accept a directory name for generate
    if command == "generate":
        if args.ui_command:
            dirname = args.ui_command.pop(0)
        cli.ui_generate(dirname, include_cfa=args.include_cfa)

    elif command == "update":

        # If we have another argument
        options = {}
        while args.ui_command:
            option = args.ui_command.pop(0)
            options = parse_option(options, option)

        # Assume directory is PWD
        cli.ui_update(dirname=".", options=options, include_cfa=args.include_cfa)
    else:
        logger.exit("%s is not a known user interface command." % command)
