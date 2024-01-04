#!/usr/bin/env python3

"""
Serve a Grype listing.json and databases over HTTP.
"""

import sys
import os
# pylint: disable=no-name-in-module
from grype_cache.server.httpserver import HttpServer
# pylint: enable=no-name-in-module


if __name__ == "__main__":
    kwargs = {}
    for var_name in (
        'base_url',
        'scheme',
        'hostname',
        'port',
        'db_url_component',
        'upstream_listing_url',
        'output_dir',
        'minimise'
    ):
        value = os.getenv(var_name.upper())
        if value is not None:
            kwargs[var_name] = value
    app = HttpServer(
        __name__,
        **kwargs
    )
    app.run()
    sys.exit(0)
