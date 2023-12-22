#!/usr/bin/env python3

"""
Serve a Grype listing.json and databases over HTTP.
"""

import sys
import os
import json

from flask import Flask
from listing import str2bool


URL_PREFIX = os.getenv("URL_PREFIX", "/")
if not URL_PREFIX.endswith('/'):
    URL_REFIX = URL_PREFIX + '/'
FS_ROOT = os.getenv("FS_ROOT", 'tests/expected-output/')
HOST = os.getenv("HOSTNAME", '127.0.0.1')
PORT = int(os.getenv("PORT", "8080"))
DEBUG = str2bool(os.getenv("DEBUG", "true"))


app = Flask(__name__)


@app.route(URL_PREFIX + "listing.json")
def serve_listing():
    """
    Serve the listing.json catalogue.
    """
    with open(
        os.path.join(FS_ROOT, "minimised.json"),
        "r",
        encoding='utf-8'
    ) as filehandle:
        return json.load(filehandle)


if __name__ == "__main__":
    app.run(
        debug=DEBUG,
        host=HOST,
        port=PORT
    )
    sys.exit(0)
