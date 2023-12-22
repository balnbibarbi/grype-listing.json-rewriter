"""
A simple HTTP server for a Grype catalogue and database files.
"""


import os
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
        self.listing = Listing(
            os.getenv("LISTING_JSON_URL", UPSTREAM_LISTING_URL)
        )
        self.listing.minimise()
        self.listing.save(os.path.join(self.fs_root, LISTING_CACHE_FILENAME))

    def run(self, *args, **kwargs):
        return super().run(
            *args, **kwargs,
            debug=True,
            host=self.hostname,
            port=self.port
        )
