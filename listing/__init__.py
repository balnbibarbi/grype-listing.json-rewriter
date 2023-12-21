"""
An Anchore Grype vulnerability database listing.json
"""


import os
import io
import sys
import json
from datetime import datetime
import logging
import requests


SRC_URL_PREFIX = 'https://toolbox-data.anchore.io/grype/databases/'
HTTP_TIMEOUT_MAX = 300


def parse_iso8601(iso8601_datetime):
    """
    Parse an ISO 8601 datetime string in format YYYY-MM-DDThh:mm:ssZ.
    """
    # return datetime.fromisoformat(iso8601_datetime)
    return datetime.strptime(iso8601_datetime, "%Y-%m-%dT%H:%M:%S%z")


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


class Listing:

    """
    An Anchore Grype vulnerability database listing.json
    """

    def __init__(self, input_url, minimal) -> None:
        self.listing = self._load_listing_json(input_url)
        if minimal:
            self.minimise_listing()

    def _find_latest_schema(self):
        """
        Find the latest of the schemas in the listing.json file.
        """
        schemas = self.listing['available']
        schema_keys = list(schemas.keys())
        schema_keys.sort()
        latest_schema_key = schema_keys[-1]
        latest_schema = schemas[latest_schema_key]
        return (latest_schema_key, latest_schema)

    @staticmethod
    def _find_latest_version(schema):
        """
        Find the latest of the versions in the schema.
        """
        latest_version_built_date = None
        latest_version = None
        for this_version in schema:
            this_version_built_date = parse_iso8601(this_version['built'])
            if (
                latest_version_built_date is None or
                this_version_built_date > latest_version_built_date
            ):
                latest_version_built_date = this_version_built_date
                latest_version = this_version
        return (latest_version_built_date, latest_version)

    @staticmethod
    def _download_version(version, output_dir):
        """
        Download a specific version of a vulnerability db.
        """
        filename = os.path.join(
            output_dir,
            version['url'].rsplit('/', 1)[-1]
        )
        download(version['url'], filename)

    def download_dbs(self, output_dir):
        """
        Optionally, download all, or only the latest, vulnerability
        database(s).
        """
        if output_dir:
            for schema in self.listing['available'].values():
                for version in schema:
                    self._download_version(version, output_dir)
        else:
            logging.info("Refraining from downloading database.")

    def output_listing_json(self, file_name):
        """
        Output a Grype style listing.json file.
        """
        logging.info(
            "Outputting listing.json to '%s'.",
            file_name
        )
        if file_name:
            with magic_open(file_name, "w") as output_file:
                print(json.dumps(self.listing), file=output_file)
        else:
            logging.info("Refraining from outputting new listing.json.")

    def minimise_listing(self):
        """
        Minimise a listing.json, so it contains only the latest database
        schema, and only the latest vulnerability database in that schema.
        """
        # Find the latest schema
        (latest_schema_key, latest_schema) = self._find_latest_schema()
        logging.debug(
            "Latest schema: %s %s",
            latest_schema_key,
            latest_schema
        )
        # Find the latest version in the latest schema
        (
            latest_version_build_date,
            latest_version
        ) = self._find_latest_version(latest_schema)
        logging.info(
            "Latest version is %s",
            latest_version_build_date
        )
        self.listing['available'] = {
            latest_schema_key: [
                latest_version
            ]
        }
        return self.listing

    def _load_listing_json(self, input_url):
        """
        Load and parse a Grype style listing.json file.
        """
        with magic_open(input_url, "r") as input_file:
            return json.load(input_file)

    def rewrite_urls(self, new_prefix):
        """
        Replace the Anchore URL prefix on the given version's
        database URL with the given URL prefix.
        """
        if new_prefix:
            logging.debug(
                "Replacing '%s' with '%s' in database URLs",
                SRC_URL_PREFIX,
                new_prefix
            )
            for schema in self.listing['available'].values():
                for version in schema:
                    new_url = version['url'].replace(
                        SRC_URL_PREFIX,
                        new_prefix
                    )
                    logging.debug(
                        "Updating URL from '%s' to '%s'",
                        version['url'],
                        new_url
                    )
                    version['url'] = new_url
        else:
            logging.info("Refraining from updating database URLs.")
