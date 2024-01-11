#!/usr/bin/env python3

"""
Serve a Grype listing.json and databases over HTTP.
"""

import sys
import os
import signal
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


def exit_gracefully(signum, frame):
    """
    Gracefully terminate the process.
    """
    if signum is not None:
        del signum
    if frame is not None:
        del frame
    sys.exit(0)


def main():
    """
    Entry point.
    """
    kwargs = {}
    for var_name in (
        'base_url',
        'bind_scheme',
        'bind_hostname',
        'bind_port',
        'public_scheme',
        'public_hostname',
        'public_port',
        'db_url_component',
        'upstream_listing_url',
        'output_dir',
        'minimise'
    ):
        value = get_param(var_name)
        if value is not None:
            kwargs[var_name] = value
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    app = HttpServer(
        __name__,
        **kwargs
    )
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
