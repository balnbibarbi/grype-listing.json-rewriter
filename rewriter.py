#!/usr/bin/python3


import sys
import json
import argparse
from datetime import datetime


LISTING_JSON_FILENAME = "listing.json"
SRC_URL_PREFIX = 'https://toolbox-data.anchore.io/grype/databases/'


def parse_iso8601(iso8601_datetime):
    # return datetime.fromisoformat(iso8601_datetime)
    return datetime.strptime(iso8601_datetime, "%Y-%m-%dT%H:%M:%S%z")


def find_latest_version(versions):
    version_keys = [ key for key in versions.keys() ]
    version_keys.sort()
    latest_version_key = version_keys[-1]
    latest_version = versions[latest_version_key]
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--urlprefix",
        help="New URL prefix to replace existing prefix",
        type=str
    )
    args = parser.parse_args()
    with open(LISTING_JSON_FILENAME, "r") as listing_file:
        listing = json.load(listing_file)
        versions = listing['available']
        (latest_version_key, latest_version) = find_latest_version(versions)
        latest_revision = find_latest_revision(latest_version)
        latest_revision['url'] = latest_revision['url'].replace(SRC_URL_PREFIX, args.urlprefix)
        print(json.dumps({
            'available': {
                latest_version_key: [ latest_revision ]
            }
        }))
    sys.exit(0)
