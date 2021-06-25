__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from contributor_ci.main import Client
import re


def main(args, parser, extra, subparser):

    client = Client(
        quiet=args.quiet,
        config_file=args.config_file,
        outdir=args.outdir,
        require_config=False,
    )

    for name, extractor in client.extractors.items():
        if not args.query:
            print("%20s: %s" % (name, extractor.description))
        elif args.query and re.search(args.query, name):
            print("%20s: %s" % (name, extractor.description))
