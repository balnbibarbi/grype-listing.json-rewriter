#!/usr/bin/env python3


"""
Download and rewrite Grype listing.json files.
These files contain a list of vulberability database versions.
Each version in turn contains a list of vulnerability database files.
"""

import os
import sys
import io
import logging
import json
import argparse
from datetime import datetime
import requests


SRC_URL_PREFIX = 'https://toolbox-data.anchore.io/grype/databases/'
HTTP_TIMEOUT_MAX = 300


def parse_iso8601(iso8601_datetime):
    """
    Parse an ISO 8601 datetime string in format YYYY-MM-DDThh:mm:ssZ.
    """
    # return datetime.fromisoformat(iso8601_datetime)
    return datetime.strptime(iso8601_datetime, "%Y-%m-%dT%H:%M:%S%z")


def find_latest_version(listing):
    """
    Find the latest of the versions in the given listing.json file.
    """
    versions = listing['available']
    version_keys = list(versions.keys())
    version_keys.sort()
    latest_version_key = version_keys[-1]
    latest_version = versions[latest_version_key]
    return (latest_version_key, latest_version)


def find_latest_revision(version):
    """
    Find the latest of the revisions in the given version.
    """
    latest_revision_built_date = None
    latest_revision = None
    for this_revision in version:
        this_revision_built_date = parse_iso8601(this_revision['built'])
        if (
            latest_revision_built_date is None or
            this_revision_built_date > latest_revision_built_date
        ):
            latest_revision_built_date = this_revision_built_date
            latest_revision = this_revision
    return (latest_revision_built_date, latest_revision)


def magic_open(filename, mode):
    """
    Open a file, URL or stdin/stdout.
    """
    logging.info("Opening '%s'...", filename)
    if filename == "-":
        if mode == "r":
            return sys.stdin
        if mode == "w":
            return sys.stdout
        return sys.stderr
    if mode == "r" and (
        filename.startswith("http://") or filename.startswith("https://")
    ):
        req = requests.get(filename, timeout=HTTP_TIMEOUT_MAX)
        req.raise_for_status()
        return io.StringIO(req.text)
    return open(filename, mode, encoding="utf-8")


def download(url, filename):
    """
    Download a URL to a local file.
    """
    logging.info("Downloading '%s' to '%s'", url, filename)
    with (open(filename, "wb")) as outfh:
        req = requests.get(url, timeout=HTTP_TIMEOUT_MAX)
        req.raise_for_status()
        outfh.write(req.content)


def download_revision(revision, output_dir):
    """
    Download a specific revision of a vulnerability db.
    """
    filename = os.path.join(
        output_dir,
        revision['url'].rsplit('/', 1)[-1]
    )
    download(revision['url'], filename)


def output_listing_json(file_name, latest_version_key, latest_revision):
    """
    Output a Grype style listing.json file.
    """
    logging.info(
        "Outputting new listing.json to '%s'.", file_name
    )
    with magic_open(file_name, "w") as output_file:
        print(json.dumps({
            'available': {
                latest_version_key: [latest_revision]
            }
        }), file=output_file)


def load_listing_json(input_url):
    """
    Load and parse a Grype style listing.json file.
    """
    with magic_open(input_url, "r") as input_file:
        listing = json.load(input_file)
        # Find the latest version
        (latest_version_key, latest_version) = find_latest_version(
            listing
        )
        logging.debug("Latest version: %s %s", latest_version_key, latest_version)
        # Find the latest revision in the latest version
        (
            latest_revision_build_date,
            latest_revision
        ) = find_latest_revision(latest_version)
        logging.info(
            "Latest revision is %s",
            latest_revision_build_date
        )
        return (latest_version_key, latest_revision)


def rewrite_revision_url(revision, new_prefix):
    """
    Replace the Anchore URL prefix on the given revision's
    database URL with the given URL prefix.
    """
    new_url = revision['url'].replace(
        SRC_URL_PREFIX,
        new_prefix
    )
    logging.debug(
        "Updating URL prefix from '%s' to '%s'",
        revision['url'],
        new_url
    )
    revision['url'] = new_url


def main():
    """
    Application entrypoint.
    """
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
    # Load the listing.json list of vulnerability database versions
    (
        latest_version_key,
        latest_revision
    ) = load_listing_json(args.input)
    # Optionally, download the latest revision
    if args.download_latest_db:
        download_revision(latest_revision, args.download_latest_db)
    else:
        logging.info("Refraining from downloading latest database.")
    # Optionally, output a minimal listing.json
    if args.output:
        # Optionally, rewrite the database URL
        if args.urlprefix:
            rewrite_revision_url(latest_revision, args.urlprefix)
        else:
            logging.info("Refraining from updating URL prefix.")
        output_listing_json(args.output, latest_version_key, latest_revision)
    else:
        logging.info("Refraining from outputting new listing.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
