"""
Time and HTTP-related utilities.
"""


import io
import sys
import os
import time
from datetime import datetime
import logging
import requests


HTTP_TIMEOUT_MAX = 300


def str2bool(v):
    """
    Convert a human-readable string to a boolean value.
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'on', 'enabled'):
        return True
    if v.lower() in ('no', 'false', 'f', 'n', '0', 'off', 'disabled'):
        return False
    raise ValueError('Boolean value expected')


def parse_iso8601(iso8601_datetime):
    """
    Parse an ISO 8601 datetime string in format YYYY-MM-DDThh:mm:ssZ.
    """
    # return datetime.fromisoformat(iso8601_datetime)
    return datetime.strptime(iso8601_datetime, "%Y-%m-%dT%H:%M:%S%z")


def magic_open(filename, mode):
    """
    Open a file, URL or stdin/stdout.
    """
    logging.info("Opening '%s'...", filename)
    if filename == "-":
        if mode == "r":
            return sys.stdin
        if mode == "w":
            return sys.stdout
        return sys.stderr
    if mode == "r" and (
        filename.startswith("http://") or filename.startswith("https://")
    ):
        req = requests.get(filename, timeout=HTTP_TIMEOUT_MAX)
        req.raise_for_status()
        return io.StringIO(req.text)
    return open(filename, mode, encoding="utf-8")


def download(url, filename):
    """
    Download a URL to a local file.
    """
    logging.info("Downloading '%s' to '%s'", url, filename)
    try:
        stat_res = os.stat(filename)
        headers = {
            'If-Modified-Since': time.strftime(
                '%a, %d %b %Y %H:%M:%S GMT',
                time.gmtime(stat_res.st_mtime)
            ),
            'Range': f'bytes={stat_res.st_size}-'
        }
    except FileNotFoundError:
        headers = {}
    with (open(filename, "a+b")) as outfh:
        req = requests.get(url, timeout=HTTP_TIMEOUT_MAX, headers=headers)
        req.raise_for_status()
        outfh.write(req.content)
        outfh.close()
