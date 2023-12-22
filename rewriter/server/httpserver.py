"""
A simple HTTP server for a Grype catalogue and database files.
"""


import os
from flask import Flask


class HttpServer(Flask):

    """
    A simple HTTP server for a Grype catalogue and database files.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url_prefix = os.getenv("URL_PREFIX", "/")
        if not self.url_prefix.endswith('/'):
            self.url_prefix = self.url_prefix + '/'
        self.fs_root = os.getenv("FS_ROOT", 'tests/expected-output/')
        self.hostname = os.getenv("HOSTNAME", '127.0.0.1')
        self.port = int(os.getenv("PORT", "8080"))

    def run(self, *args, **kwargs):
        return super().run(
            *args, **kwargs,
            debug=False,
            host=self.hostname,
            port=self.port
        )
