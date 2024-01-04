#!/usr/bin/env python3

"""
Serve a Grype listing.json and databases over HTTP.
"""

import sys
import os
# pylint: disable=no-name-in-module
from grype_cache.server.httpserver import HttpServer
# pylint: enable=no-name-in-module


def get_param(var_name):
    """
    Retrieve the value of the given-named parameter.
    Parameter names are converted to uppercase,
    then looked up in the process environment.
    """
    return os.getenv(var_name.upper())


def main():
    """
    Entry point.
    """
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
        value = get_param(var_name)
        if value is not None:
            kwargs[var_name] = value
    app = HttpServer(
        __name__,
        **kwargs
    )
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
