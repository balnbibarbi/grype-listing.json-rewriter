"""
A simple HTTP server for a Grype catalogue and database files.
"""


import sys
import os
import requests
from flask import Flask
# pylint: disable=no-name-in-module
from rewriter.listing.listing import Listing
# pylint: enable=no-name-in-module


UPSTREAM_LISTING_URL = (
    "https://toolbox-data.anchore.io/grype/databases/listing.json"
)
LISTING_CACHE_FILENAME = "listing.json"


class HttpServer(Flask):

    """
    A simple HTTP server for a Grype catalogue and database files.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_prefix = os.getenv("URL_PREFIX", "/")
        if not self.url_prefix.endswith('/'):
            self.url_prefix = self.url_prefix + '/'
        self.fs_root = os.getenv("FS_ROOT", '/tmp')
        self.hostname = os.getenv("HOSTNAME", '127.0.0.1')
        self.port = int(os.getenv("PORT", "8080"))
        self.cache_filename = os.path.join(
            self.fs_root,
            LISTING_CACHE_FILENAME
        )
        self.upstream_listing_url = os.getenv(
            "LISTING_JSON_URL",
            UPSTREAM_LISTING_URL
        )
        try:
            self.listing = Listing(self.upstream_listing_url)
        except requests.exceptions.RequestException as url_error:
            print(url_error, file=sys.stderr)
            try:
                self.listing = Listing(self.cache_filename)
            except (FileNotFoundError, PermissionError) as cache_error:
                print(cache_error, file=sys.stderr)
                self.listing = None
        if self.listing is not None:
            self.listing.minimise()
            self.listing.save(self.cache_filename)

    def refresh(self):
        """
        Reload the upstream listing.json, and replace our cached copy with it.
        """
        new_listing = Listing(self.upstream_listing_url)
        new_listing.minimise()
        new_listing.save(self.cache_filename)
        self.listing = new_listing

    def run(self, *args, **kwargs):
        return super().run(
            *args, **kwargs,
            debug=True,
            host=self.hostname,
            port=self.port
        )
