"""
A cache for an Anchore Grype vulnerability database.
"""


import os
import logging
import json
import requests
from ..listing.listing import Listing
from ..utils import magic_open, download


LISTING_CACHE_FILENAME = "listing.json"
DEFAULT_DATA_DIR = '/tmp'
UPSTREAM_LISTING_JSON_URL = (
    "https://toolbox-data.anchore.io/grype/databases/listing.json"
)


class Cache:

    """
    A cache for an Anchore Grype vulnerability database.
    """

    def __init__(
        self,
        db_url_prefix,
        output_dir=DEFAULT_DATA_DIR,
        listing_json_url=UPSTREAM_LISTING_JSON_URL,
        minimise=True
    ):
        self.db_url_prefix = db_url_prefix
        self.output_dir = output_dir
        self.listing_json_url = listing_json_url
        self.listing_filename = os.path.join(
            self.output_dir,
            LISTING_CACHE_FILENAME
        )
        self.minimise = minimise
        self.listing = None
        # This delays initialisation too much, so is left to do lazily later
        # self.refresh()

    def set_listing(self, new_listing):
        """
        Replace the current listing by the given one.
        """
        if new_listing is None:
            return
        if self.minimise:
            new_listing.minimise()
        # Download the databases before writing the new listing to disk,
        # in the hope (not enforced) that the the on-disk listing
        # never refers to a nonexistent database.
        # This could be enforced using fsync, at some performance cost.
        self._download_listing_dbs(new_listing, self.output_dir)
        if self.db_url_prefix:
            new_listing.rewrite_urls(self.db_url_prefix)
        logging.debug("Writing listing to '%s'", self.listing_filename)
        self._save_listing(new_listing, self.listing_filename)
        old_listing = self.listing
        self.listing = new_listing
        # Remove now-unreferenced database files
        if old_listing:
            old_filenames = set(old_listing.db_filenames())
            new_filenames = set(new_listing.db_filenames())
            unreferenced_filenames = old_filenames - new_filenames
            for db_filename in unreferenced_filenames:
                db_path = os.path.join(
                    self.output_dir,
                    db_filename
                )
                logging.debug(
                    "Deleting no-longer-referenced database '%s'",
                    db_path
                )
                os.unlink(db_path)

    def refresh(self):
        """
        Try to reload the listing and databases from the upstream source.
        """
        try:
            # Try to load the listing from upstream
            new_listing = self._load_listing(self.listing_json_url)
            self.set_listing(new_listing)
        except requests.exceptions.RequestException as url_error:
            # Fall back to loading listing from local cache
            logging.error(url_error)
            if not self.listing:
                new_listing = self._load_listing(self.listing_filename)
                self.set_listing(new_listing)

    def get_listing(self):
        """
        Return a (possibly cached) copy of the listing.
        """
        self.refresh()
        return self.listing

    @staticmethod
    def _download_listing_dbs(listing, output_dir):
        """
        Download all vulnerability databases in the given listing
        to the given output directory.
        """
        for db_tuple in listing.db_urls_and_filenames():
            (db_url, db_filename) = db_tuple
            db_path = os.path.join(
                output_dir,
                db_filename
            )
            download(db_url, db_path)

    def download_dbs(self):
        """
        Download all vulnerability databases.
        """
        self._download_listing_dbs(self.listing, self.output_dir)

    @staticmethod
    def _load_listing(input_url):
        """
        Load and parse a Grype style listing.json file.
        """
        with magic_open(input_url, "r") as input_file:
            return Listing(json.load(input_file))

    @staticmethod
    def _save_listing(listing, file_name):
        """
        Output the listing to a json file.
        """
        logging.info(
            "Outputting listing json to '%s'.",
            file_name
        )
        with magic_open(file_name, "w") as output_file:
            print(listing.json(), file=output_file)

    def rewrite_urls(self, new_prefix):
        """
        Rewrite the listing's database URLs,
        so they all begin with the given URL prefix.
        """
        self.listing.rewrite_urls(new_prefix)
