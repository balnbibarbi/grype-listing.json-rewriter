"""
An Anchore Grype vulnerability database listing.json
"""


import os
import json
import logging
from ..utils import parse_iso8601, magic_open, download


SRC_URL_PREFIX = 'https://toolbox-data.anchore.io/grype/'


class Listing:

    """
    An Anchore Grype vulnerability database listing.json
    """

    def __init__(self, input_url):
        self.listing = self._load_listing_json(input_url)

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

    def schemas(self):
        """
        Return the collection of Grype vulnerability database
        schema versions in this listing.
        """
        return self.listing['available']

    def db_urls(self):
        """
        Enumerate over all databse URLs in this listing.
        """
        for schema in self.schemas().values():
            for version in schema:
                yield version['url']

    def download_dbs(self, output_dir):
        """
        Optionally, download all vulnerability databases.
        """
        if output_dir:
            for schema in self.schemas().values():
                for version in schema:
                    self._download_version(version, output_dir)
        else:
            logging.info("Refraining from downloading database.")

    def json(self):
        """
        Return the Grype JSON representation of this listing.
        """
        return json.dumps(self.listing)

    def save(self, file_name):
        """
        Output a Grype style listing.json file.
        """
        logging.info(
            "Outputting listing.json to '%s'.",
            file_name
        )
        if file_name:
            with magic_open(file_name, "w") as output_file:
                print(self.json(), file=output_file)
        else:
            logging.info("Refraining from outputting new listing.json.")

    def _find_latest_schema(self):
        """
        Find the latest of the schemas in the listing.json file.
        """
        schemas = self.schemas()
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

    def minimise(self):
        """
        Minimise this listing, so it contains only the latest database
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
            for schema in self.schemas().values():
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
