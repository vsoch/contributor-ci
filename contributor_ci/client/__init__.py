#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

import argparse
import os
import sys

import contributor_ci
from contributor_ci.logger import setup_logger


def get_parser():
    parser = argparse.ArgumentParser(
        description="Contributor CI",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--debug",
        dest="debug",
        help="use verbose logging to debug.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--quiet",
        dest="quiet",
        help="suppress additional output.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-c",
        "--config-file",
        dest="config_file",
        help="custom path to contributor-ci.yaml file.",
        default="contributor-ci.yaml",
    )

    parser.add_argument(
        "-o",
        "--out-dir",
        dest="outdir",
        help="Specify a custom output directory (defaults to $PWD/.cci)",
        default=None,
    )

    parser.add_argument(
        "--version",
        dest="version",
        help="suppress additional output.",
        default=False,
        action="store_true",
    )

    description = "actions for Contributor CI"
    subparsers = parser.add_subparsers(
        help="contributor-ci actions",
        title="actions",
        description=description,
        dest="command",
    )

    # print version and exit
    subparsers.add_parser("version", help="show software version")
    init = subparsers.add_parser("init", help="Create a contributor-ci.yaml.")
    init.add_argument("username", help="GitHub user or org name to base off of.")

    cfa = subparsers.add_parser("cfa", help="Contributor Friendliness Assessment")
    cfa.add_argument(
        "-t",
        "--terminal",
        action="store_true",
        default=False,
        help="print output to the terminal.",
    )
    cfa.add_argument(
        "repo", help="repository or 'all' to run for a contributor-ci.yaml file."
    )

    config = subparsers.add_parser(
        "config",
        description="update configuration file. Use sort, edit, add, or remove to edit fields.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    config.add_argument(
        "params",
        nargs="*",
        help="edit, add, remove, or sort",
        type=str,
    )

    # See extractors
    listing = subparsers.add_parser(
        "list",
        description="see extractors available",
    )

    listing.add_argument(
        "query",
        help="search extractors by a query string",
        nargs="?",
        default=None,
    )
    # Local shell with client loaded
    shell = subparsers.add_parser(
        "shell", help="shell into a Python session with a client."
    )
    shell.add_argument("module_name", help="module to inspect", nargs="?")
    shell.add_argument(
        "--interpreter",
        "-i",
        dest="interpreter",
        help="python interpreter",
        choices=["ipython", "python", "bpython"],
        default="ipython",
    )

    # Extract metrics for a repository
    extract = subparsers.add_parser(
        "extract", description="extract metrics for a repository."
    )
    extract.add_argument("method", help="extraction method", nargs="*")
    extract.add_argument(
        "--save-format",
        dest="save_format",
        help="use a custom save format (e.g., year/month) defaults to year/month/day",
    )

    # Generate an interface with extractions, a GitHub workflow to run updates,
    # and contributor friendliness files.
    ui = subparsers.add_parser(
        "ui", description="generate or update a CCI user interface."
    )
    ui.add_argument("ui_command", help="generate or update.", nargs="*")
    ui.add_argument(
        "--cfa",
        dest="include_cfa",
        help="include contributor friendliness assessments for generate or update.",
        default=False,
        action="store_true",
    )

    return parser


def run():
    parser = get_parser()

    def help(return_code=0):
        """print help, including the software version and active client
        and exit with return code.
        """

        version = contributor_ci.__version__

        print("\nContributor CI v%s" % version)
        parser.print_help()
        sys.exit(return_code)

    # If the user didn't provide any arguments, show the full help
    if len(sys.argv) == 1:
        help()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    if args.debug is True:
        os.environ["MESSAGELEVEL"] = "DEBUG"

    # Show the version and exit
    if args.command == "version" or args.version:
        print(contributor_ci.__version__)
        sys.exit(0)

    setup_logger(
        quiet=args.quiet,
        debug=args.debug,
    )

    # retrieve subparser (with help) from parser
    helper = None
    subparsers_actions = [
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ]
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            if choice == args.command:
                helper = subparser
                break

    if args.command == "cfa":
        from .cfa import main
    elif args.command == "extract":
        from .extract import main
    elif args.command == "init":
        from .init import main
    elif args.command == "list":
        from .listing import main
    elif args.command == "shell":
        from .shell import main
    elif args.command == "config":
        from .config import main
    elif args.command == "ui":
        from .ui import main

    # Pass on to the correct parser
    return_code = 0
    try:
        main(args=args, parser=parser, extra=extra, subparser=helper)
        sys.exit(return_code)
    except UnboundLocalError:
        return_code = 1

    help(return_code)


if __name__ == "__main__":
    run()
