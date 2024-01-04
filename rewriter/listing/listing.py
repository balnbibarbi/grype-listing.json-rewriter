"""
An Anchore Grype vulnerability database listing.json
"""


import json
import logging
from ..utils import parse_iso8601


class Listing:

    """
    An Anchore Grype vulnerability database listing.json
    """

    def __init__(self, listing_data):
        self.listing = listing_data

    def schemas(self):
        """
        Return the collection of Grype vulnerability database
        schema versions in this listing.
        """
        return self.listing['available']

    @staticmethod
    def _db_url_to_filename(db_url):
        """
        Convert a database URL into just the filename.
        """
        return db_url.rsplit('/', 1)[-1]

    def db_urls(self):
        """
        Enumerate over all database URLs in this listing.
        """
        for schema in self.schemas().values():
            for version in schema:
                yield version['url']

    def db_filenames(self):
        """
        Enumerate over all database filenames in this listing.
        """
        for db_url in self.db_urls():
            yield self._db_url_to_filename(db_url)

    def db_urls_and_filenames(self):
        """
        Enumerate over all databases in this listing,
        returning for each a (url, filename) tuple.
        """
        for schema in self.schemas().values():
            for version in schema:
                db_url = version['url']
                yield (db_url, self._db_url_to_filename(db_url))

    def json(self):
        """
        Return the Grype JSON representation of this listing.
        """
        return json.dumps(self.listing)

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
        # logging.debug(
        #     "Latest schema: %s %s",
        #     latest_schema_key,
        #     latest_schema
        # )
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

    def rewrite_urls(self, new_prefix):
        """
        Replace everything before the filename in each
        database URL with the given URL prefix.
        """
        try:
            db_url = next(self.db_urls())
        except StopIteration:
            # No database URLs to rewrite
            return
        old_prefix = db_url.rsplit('/', 1)[0]
        logging.debug(
            "Replacing '%s' with '%s' in database URLs",
            old_prefix,
            new_prefix
        )
        for schema in self.schemas().values():
            for version in schema:
                new_url = version['url'].replace(
                    old_prefix,
                    new_prefix
                )
                version['url'] = new_url
