#!/usr/bin/env python3


"""
Download and rewrite Grype listing.json files.
These files contain a list of vulnerability database schemas.
Each schema in turn contains a list of vulnerability database versions.
"""

import sys
import logging
import argparse
from grype_cache.cache.cache import Cache
from grype_cache.utils import str2bool


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
    cache_args = {}
    if args.download_dbs:
        cache_args['fs_root'] = args.download_dbs
    if args.minimal:
        cache_args['minimise'] = True
    cache = Cache(args.url_prefix, listing_json_url=args.input, **cache_args)
    cache.refresh()
    return 0


if __name__ == "__main__":
    sys.exit(main())
