#!/usr/bin/env python3

"""
Serve a Grype listing.json and databases over HTTP.
"""

import sys
# pylint: disable=no-name-in-module
from rewriter.server.httpserver import HttpServer
# pylint: enable=no-name-in-module


app = HttpServer(__name__)


@app.route(app.url_prefix + "listing.json")
def serve_listing():
    """
    Serve the listing.json catalogue.
    """
    if app.listing is None:
        app.refresh()
    if app.listing is None:
        return '{}'
    return app.listing.json()


@app.route(app.url_prefix + "refresh")
def refresh_listing():
    """
    Attempt to download a new listing.json from the upstream source.
    """
    # pylint: disable=broad-exception-caught
    try:
        app.refresh()
        return ""
    except Exception as e:
        print(e, file=sys.stderr)
        return e
    # pylint: enable=broad-exception-caught


if __name__ == "__main__":
    app.run()
    sys.exit(0)
