"""
A simple HTTP server for a Grype catalogue and database files.
"""


from urllib.parse import urlunparse
import logging
from flask import Flask, send_from_directory
# pylint: disable=no-name-in-module
from rewriter.cache.cache import Cache
# pylint: enable=no-name-in-module
# pylint: disable=fixme


DEFAULT_BASE_URL = '/'
DEFAULT_HOSTNAME = '127.0.0.1'
DEFAULT_PORT = 8080
DEFAULT_SCHEME = 'http'
DEFAULT_DB_SUBDIR = 'databases'


logging.basicConfig(level=logging.DEBUG)


class HttpServer(Flask):

    """
    A simple HTTP server for a Grype catalogue and database files.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        package_name,
        base_url=DEFAULT_BASE_URL,
        scheme=DEFAULT_SCHEME,
        hostname=DEFAULT_HOSTNAME,
        port=DEFAULT_PORT,
        db_subdir=DEFAULT_DB_SUBDIR
    ):
        super().__init__(package_name)
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
                base_url,
                '',
                '',
                ''
            )
        )
        self.add_url_rule(
            base_url + "listing.json",
            view_func=self.view_listing
        )
        self.add_url_rule(
            base_url + "refresh",
            view_func=self.view_listing
        )
        self.add_url_rule(
            base_url + db_subdir + '/<db_file>',
            view_func=self.view_download_db
        )
        self.config['SERVER_NAME'] = netloc
        self.config['APPLICATION_ROOT'] = base_url
        self.config['PREFERRED_URL_SCHEME'] = scheme
        sample_db_url = self.url_for('view_download_db', db_file='somedb.gz')
        db_url_prefix = sample_db_url.rsplit('/', 1)[0]
        self.cache = Cache(db_url_prefix)

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

    def view_listing(self):
        """
        Attempt to refresh the listing, then serve it.
        """
        return self.cache.get_listing().json()

    def view_download_db(self, db_file):
        """
        Serve a vulnerability database.
        """
        return send_from_directory(self.cache.fs_root, db_file)
