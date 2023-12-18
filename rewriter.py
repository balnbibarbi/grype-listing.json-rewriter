#!/usr/bin/env python3


import os
import sys
import io
import logging
import json
import argparse
import requests
from datetime import datetime


SRC_URL_PREFIX = 'https://toolbox-data.anchore.io/grype/databases/'


def parse_iso8601(iso8601_datetime):
    # return datetime.fromisoformat(iso8601_datetime)
    return datetime.strptime(iso8601_datetime, "%Y-%m-%dT%H:%M:%S%z")


def find_latest_version(versions):
    version_keys = [ key for key in versions.keys() ]
    version_keys.sort()
    latest_version_key = version_keys[-1]
    latest_version = versions[latest_version_key]
    logging.debug("Latest version: %s %s" % (latest_version_key, latest_version))
    return (latest_version_key, latest_version)


def find_latest_revision(version):
    latest_revision_built_date = None
    latest_revision = None
    for this_revision in version:
        this_revision_built_date = parse_iso8601(this_revision['built'])
        if latest_revision_built_date is None or this_revision_built_date > latest_revision_built_date:
            latest_revision_built_date = this_revision_built_date
            latest_revision = this_revision
    return latest_revision


def magic_open(filename, mode):
    logging.debug("Magic opening '%s'..." % filename)
    if filename == "-":
        if mode == "r":
            return sys.stdin
        elif mode == "w":
            return sys.stdout
        else:
            return sys.stderr
    elif mode == "r" and (
        filename.startswith("http://") or filename.startswith("https://")
    ):
        req = requests.get(filename)
        req.raise_for_status()
        return io.StringIO(req.text)
    else:
        return open(filename, mode)


def download(url, filename):
    logging.info("Downloading '%s' to '%s'" % (url, filename))
    with(open(filename, "wb")) as outfh:
        req = requests.get(url)
        req.raise_for_status()
        outfh.write(req.content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--urlprefix",
        help="New URL prefix to replace existing prefix",
        default="",
        type=str
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Input listing.json file or URL",
        default="-",
        type=str
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output listing.json file",
        default="-",
        type=str
    )
    parser.add_argument(
        "-d",
        "--download-latest-db",
        help="Download the latest database file to this directory",
        default="",
        type=str
    )
    parser.add_argument(
        "-r",
        "--rewrite-listing-json",
        help="Output a modified listing.json",
        default=True,
        type=bool
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Output debugging messages",
        default=False,
        action='store_true'
    )
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    with magic_open(args.input, "r") as input_file:
        with magic_open(args.output, "w") as output_file:
            listing = json.load(input_file)
            versions = listing['available']
            (latest_version_key, latest_version) = find_latest_version(versions)
            latest_revision = find_latest_revision(latest_version)
            if args.download_latest_db:
                filename = os.path.join(args.download_latest_db, latest_revision['url'].rsplit('/', 1)[-1])
                download(latest_revision['url'], filename)
            if args.urlprefix:
                new_url = latest_revision['url'].replace(SRC_URL_PREFIX, args.urlprefix)
                logging.debug("Updating URL prefix from '%s' to '%s'" % (latest_revision['url'], new_url))
                latest_revision['url'] = new_url
            if args.rewrite_listing_json:
                logging.debug("Outputting new listing.json:")
                print(json.dumps({
                    'available': {
                        latest_version_key: [ latest_revision ]
                    }
                }), file=output_file)
    sys.exit(0)
