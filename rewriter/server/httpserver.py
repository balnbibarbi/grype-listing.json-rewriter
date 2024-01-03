"""
A simple HTTP server for a Grype catalogue and database files.
"""


import os
from urllib.parse import urlunparse
import logging
import requests
from flask import Flask, send_from_directory, abort
# pylint: disable=no-name-in-module
from rewriter.listing.listing import Listing
# pylint: enable=no-name-in-module
# pylint: disable=fixme


UPSTREAM_LISTING_JSON_URL = (
    "https://toolbox-data.anchore.io/grype/databases/listing.json"
)
DEFAULT_CACHE_FILENAME = "listing.json"
DEFAULT_URL_PREFIX = '/'
DEFAULT_HOSTNAME = '127.0.0.1'
DEFAULT_PORT = 8080
DEFAULT_SCHEME = 'http'
DEFAULT_DB_SUBDIR = 'databases'
DEFAULT_FS_ROOT = '/tmp'


logging.basicConfig(level=logging.DEBUG)


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
        scheme=DEFAULT_SCHEME,
        hostname=DEFAULT_HOSTNAME,
        port=DEFAULT_PORT,
        fs_root=DEFAULT_FS_ROOT,
        db_subdir=DEFAULT_DB_SUBDIR,
        cache_filename=DEFAULT_CACHE_FILENAME
    ):
        super().__init__(package_name)
        self.listing_json_url = listing_json_url
        self.fs_root = fs_root
        self.hostname = hostname
        self.port = port
        if self.port is None:
            netloc = self.hostname
        else:
            netloc = self.hostname + ':' + str(self.port)
        self.base_url = urlunparse(
            (
                scheme,
                netloc,
                url_prefix,
                '',
                '',
                ''
            )
        )
        self.cache_filename = os.path.join(
            self.fs_root,
            cache_filename
        )
        self.add_url_rule(
            url_prefix + "listing.json",
            view_func=self.view_listing
        )
        self.add_url_rule(
            url_prefix + "refresh",
            view_func=self.view_listing
        )
        self.add_url_rule(
            url_prefix + "/" + db_subdir + '/<db_file>',
            view_func=self.view_download_db
        )
        self.listing = None
        try:
            # Try to load the listing from upstream
            new_listing = Listing(self.listing_json_url)
        except requests.exceptions.RequestException as url_error:
            # Fall back to loading listing from local cache
            logging.error(url_error)
            try:
                new_listing = Listing(self.cache_filename)
            except (FileNotFoundError, PermissionError) as cache_error:
                # No upstream and no local cache, so no listing
                logging.error(cache_error)
                new_listing = None
        self.update_listing(new_listing)
        self.config['SERVER_NAME'] = netloc
        self.config['APPLICATION_ROOT'] = url_prefix
        self.config['PREFERRED_URL_SCHEME'] = scheme

    def listing_url(self):
        """
        Return the URL for the listing.
        """
        return self.url_for('view_listing')

    def run(self, *args, **kwargs):
        """
        Flask entry point. Runs the web application.
        """
        return super().run(
            *args, **kwargs,
            debug=True,
            host=self.hostname,
            port=self.port
        )

    def update_listing(self, new_listing):
        """
        Replace the current listing by the given one.
        """
        if new_listing is None:
            return
        new_listing.minimise()
        new_listing.rewrite_urls(self.base_url)
        # TODO: Download the databases before writing the listing,
        # in the hope (not enforced) that the the on-disk listing
        # never refers to a nonexistent database.
        # This could be enforced using fsync, at some performance cost.
        # FIXME: Currently fails, because we rewrite the URLs too early.
        # new_listing.download_dbs(self.fs_root)
        logging.debug("Writing listing to '%s'", self.cache_filename)
        new_listing.save(self.cache_filename)
        self.listing = new_listing

    def view_listing(self):
        """
        Attempt to refresh the listing, then serve it.
        """
        try:
            new_listing = Listing(self.listing_json_url)
            self.update_listing(new_listing)
        except requests.exceptions.RequestException as url_error:
            logging.error("Failed to refresh listing")
            logging.error(url_error)
            if self.listing is None:
                # We don't have a cached listing, so this is fatal
                abort(
                    502,
                    {
                        'error': url_error,
                        'message': (
                            'Failed to read upstream listing,'
                            ' and no local cache exists'
                        )
                    }
                )
            # Fall back to serving cached listing
        return self.listing.json()

    def view_download_db(self, db_file):
        """
        Serve a vulnerability database.
        """
        return send_from_directory(self.fs_root, db_file)
