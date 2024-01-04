#!/usr/bin/env python3

"""
Serve a Grype listing.json and databases over HTTP.
"""

import sys
import os
# pylint: disable=no-name-in-module
from grype_cache.server.httpserver import HttpServer
# pylint: enable=no-name-in-module


kwargs = {}
for var_name in (
    'url_prefix',
    'fs_root',
    'hostname',
    'port',
    'listing_json_url',
    'cache_filename'
):
    value = os.getenv(var_name.upper())
    if value is not None:
        kwargs[var_name] = value
app = HttpServer(
    __name__,
    **kwargs
)


if __name__ == "__main__":
    app.run()
    sys.exit(0)
