"""
A simple HTTP server for a Grype catalogue and database files.
"""


import logging
from urllib.parse import ParseResult
from flask import Flask, send_from_directory
# pylint: disable=no-name-in-module
from grype_cache.cache.cache import Cache
# pylint: enable=no-name-in-module
from ..utils import str2bool


DEFAULT_BASE_URL = '/'
DEFAULT_BIND_HOSTNAME = '0.0.0.0'
DEFAULT_PUBLIC_HOSTNAME = '127.0.0.1'
DEFAULT_BIND_PORT = 8080
DEFAULT_PUBLIC_PORT = 8080
DEFAULT_BIND_SCHEME = 'http'
DEFAULT_PUBLIC_SCHEME = 'http'
DEFAULT_DB_URL_COMPONENT = 'databases'
DEFAULT_CACHED_LISTING_URL = 'listing.json'
LIVENESS_URL = 'healthz'


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
        bind_scheme=DEFAULT_BIND_SCHEME,
        public_scheme=DEFAULT_PUBLIC_SCHEME,
        bind_hostname=DEFAULT_BIND_HOSTNAME,
        public_hostname=DEFAULT_PUBLIC_HOSTNAME,
        bind_port=DEFAULT_BIND_PORT,
        public_port=DEFAULT_PUBLIC_PORT,
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
        self.bind_scheme = bind_scheme
        self.bind_hostname = bind_hostname
        self.bind_port = bind_port
        self.db_url_component = db_url_component
        self.public_base_url = ParseResult(
            public_scheme,
            public_hostname + ':' + str(public_port),
            base_url,
            "",
            "",
            ""
        )
        self.cached_listing_url = cached_listing_url
        self.add_url_rule(
            self.relativise_url(
                self.public_listing_url()
            ).geturl(),
            view_func=self.view_listing,
            subdomain=None
        )
        self.add_url_rule(
            self.relativise_url(
                self.public_liveness_url()
            ).geturl(),
            view_func=self.view_liveness,
            subdomain=None
        )
        # Flask needs a pattern variable appended to its URL, and requires
        # relative URLs.
        self.add_url_rule(
            self.relativise_url(
                self.public_db_pattern()
            ).geturl(),
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
        self.config['PREFERRED_URL_SCHEME'] = public_scheme
        self.cache = Cache(
            # Our clients need the public absolute URL prefix
            # (with no Flask pattern variables).
            self.public_db_prefix().geturl(),
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

    def public_url_for(self, *path_components):
        """
        Return the public URL for the given path.
        """
        return self.public_base_url._replace(
            path=self.public_base_url.path + '/'.join(
                path_components
            )
        )

    @staticmethod
    def relativise_url(url):
        """
        Convert an absolute URL to a relative one.
        """
        return url._replace(
            scheme='',
            netloc=''
        )

    def public_listing_url(self):
        """
        Return the public URL for the listing.
        """
        return self.public_url_for(
            self.cached_listing_url
        )

    def public_liveness_url(self):
        """
        Return the URL for the liveness check.
        """
        return self.public_url_for(
            LIVENESS_URL
        )

    def public_db_prefix(self):
        """
        Return the public URL prefix for database files.
        """
        return self.public_url_for(self.db_url_component)

    def public_db_pattern(self):
        """
        Return the public URL pattern for database files.
        """
        return self.public_url_for(self.db_url_component, '<db_file>')

    def run(self, *args, **kwargs):
        """
        Flask entry point. Runs the web application.
        """
        return super().run(
            *args, **kwargs,
            debug=True,
            host=self.bind_hostname,
            port=self.bind_port
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

    def view_liveness(self):
        """
        Serve a successful response.
        """
        return ""
