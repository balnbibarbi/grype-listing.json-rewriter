"""
A simple HTTP server for a Grype catalogue and database files.
"""


import logging
from flask import Flask, send_from_directory
# pylint: disable=no-name-in-module
from grype_cache.cache.cache import Cache
# pylint: enable=no-name-in-module
# pylint: disable=fixme
from ..utils import str2bool


DEFAULT_BASE_URL = '/'
DEFAULT_CACHED_LISTING_URL = 'listing.json'
DEFAULT_HOSTNAME = '0.0.0.0'
DEFAULT_PORT = 8080
DEFAULT_SCHEME = 'http'
DEFAULT_DB_URL_COMPONENT = 'databases'


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
        db_url_component=DEFAULT_DB_URL_COMPONENT,
        upstream_listing_url=None,
        output_dir=None,
        minimise=None,
        cached_listing_url=DEFAULT_CACHED_LISTING_URL
    ):
        super().__init__(
            package_name,
            subdomain_matching=False,
            static_url_path=base_url + db_url_component,
            static_folder=output_dir,
            root_path=base_url,
            host_matching=False,
            template_folder=None
        )
        self.hostname = hostname
        self.port = port
        self.base_url = base_url
        self.cached_listing_url = cached_listing_url
        db_url_prefix = self.base_url + db_url_component
        self.add_url_rule(
            self.listing_url(),
            view_func=self.view_listing,
            subdomain=None
        )
        self.add_url_rule(
            db_url_prefix + '/<db_file>',
            view_func=self.view_download_db,
            subdomain=None
        )
        # Setting SERVER_NAME causes Flask to validate incoming Host headers,
        # even when host_matching=False.
        # We must not validate incoming Host headers, because we have no idea
        # of the request path (involving potential layer 4 and 7 rewriting)
        # that leads to this service. The hostname that clients use to reach
        # us, which they quote in their 'Host' headers, bears no relation
        # to the local hostname or IP address that we're bound to.
        # Consequently SERVER_NAME must not be set.
        # However, when SERVER_NAME is not set, flask is unable to generate
        # self-referential URLs outside of a request context.
        # So we cannot use flask's url_for below.
        # self.config['SERVER_NAME'] = netloc
        self.config['APPLICATION_ROOT'] = base_url
        self.config['PREFERRED_URL_SCHEME'] = scheme
        self.cache = Cache(
            db_url_prefix,
            **(
                {} if upstream_listing_url is None else {
                    "listing_json_url": upstream_listing_url
                }
            ),
            **(
                {} if output_dir is None else {
                    "output_dir": output_dir
                }
            ),
            **(
                {} if minimise is None else {
                    "minimise": str2bool(minimise)
                }
            )
        )

    def listing_url(self):
        """
        Return the URL for the listing.
        """
        return self.base_url + self.cached_listing_url

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
        return send_from_directory(self.cache.output_dir, db_file)
