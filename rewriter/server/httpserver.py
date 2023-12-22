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


UPSTREAM_LISTING_JSON_URL = (
    "https://toolbox-data.anchore.io/grype/databases/listing.json"
)
DEFAULT_CACHE_FILENAME = "listing.json"
DEFAULT_URL_PREFIX = '/'
DEFAULT_PORT = 8080
DEFAULT_FS_ROOT = '/tmp'
DEFAULT_HOSTNAME = '127.0.0.1'


class HttpServer(Flask):

    """
    A simple HTTP server for a Grype catalogue and database files.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        package_name,
        url_prefix=DEFAULT_URL_PREFIX,
        listing_json_url=UPSTREAM_LISTING_JSON_URL,
        hostname=DEFAULT_HOSTNAME,
        port=DEFAULT_PORT,
        fs_root=DEFAULT_FS_ROOT,
        cache_filename=DEFAULT_CACHE_FILENAME
    ):
        super().__init__(package_name)
        self.listing_json_url = listing_json_url
        self.url_prefix = url_prefix
        self.fs_root = fs_root
        self.url_prefix = url_prefix
        self.hostname = hostname
        self.port = port
        if not self.url_prefix.endswith('/'):
            self.url_prefix = self.url_prefix + '/'
        self.cache_filename = os.path.join(
            self.fs_root,
            cache_filename
        )
        try:
            self.listing = Listing(self.listing_json_url)
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
        self.add_url_rule(
            self.url_prefix + "listing.json",
            view_func=self.serve_listing
        )
        self.add_url_rule(
            self.url_prefix + "refresh",
            view_func=self.refresh
        )

    def refresh(self):
        """
        Reload the upstream listing.json, and replace our cached copy with it.
        """
        new_listing = Listing(self.listing_json_url)
        new_listing.minimise()
        new_listing.save(self.cache_filename)
        self.listing = new_listing
        return ""

    def run(self, *args, **kwargs):
        return super().run(
            *args, **kwargs,
            debug=True,
            host=self.hostname,
            port=self.port
        )

    def serve_listing(self):
        """
        Serve the listing.json catalogue.
        """
        if self.listing is None:
            self.refresh()
        if self.listing is None:
            return '{}'
        return self.listing.json()
