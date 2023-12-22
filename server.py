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
    return app.listing.json()


if __name__ == "__main__":
    app.run()
    sys.exit(0)
