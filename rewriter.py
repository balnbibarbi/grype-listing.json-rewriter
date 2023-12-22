#!/usr/bin/env python3


"""
Download and rewrite Grype listing.json files.
These files contain a list of vulnerability database schemas.
Each schema in turn contains a list of vulnerability database versions.
"""

import sys
import logging
import argparse
from rewriter.listing.listing import Listing
from rewriter.utils import str2bool


def main():
    """
    Application entrypoint.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--download-dbs",
        help="""
        Download vulnerability database file(s) to this directory.
        If not specified, do not download database files.
        """,
        default="",
        type=str
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Read input listing.json from this file or URL",
        default="-",
        type=str
    )
    parser.add_argument(
        "-m",
        "--minimal",
        help="Only output/download latest database schema and version",
        default=True,
        type=str2bool
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output a listing.json file to this path",
        default="-",
        type=str
    )
    parser.add_argument(
        "-u",
        "--url-prefix",
        help="New URL prefix to replace existing prefix",
        default="",
        type=str
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Output debugging messages",
        default=False,
        type=str2bool
    )
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    # Load the listing.json list of vulnerability database schemas
    listing = Listing(args.input)
    # Optionally, subset the listing to only the latest schema and version
    if args.minimal:
        listing.minimise()
    # Optionally, download vulnerability database(s)
    listing.download_dbs(args.download_dbs)
    # Optionally, rewrite the database URLs in the listing
    listing.rewrite_urls(args.url_prefix)
    # Optionally, output a listing.json
    listing.save(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
