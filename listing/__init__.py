import os
import io
import json
from datetime import datetime
import logging
import requests


SRC_URL_PREFIX = 'https://toolbox-data.anchore.io/grype/databases/'
HTTP_TIMEOUT_MAX = 300


def parse_iso8601(iso8601_datetime):
    """
    Parse an ISO 8601 datetime string in format YYYY-MM-DDThh:mm:ssZ.
    """
    # return datetime.fromisoformat(iso8601_datetime)
    return datetime.strptime(iso8601_datetime, "%Y-%m-%dT%H:%M:%S%z")


def find_latest_schema(listing):
    """
    Find the latest of the schemas in the given listing.json file.
    """
    schemas = listing['available']
    schema_keys = list(schemas.keys())
    schema_keys.sort()
    latest_schema_key = schema_keys[-1]
    latest_schema = schemas[latest_schema_key]
    return (latest_schema_key, latest_schema)


def find_latest_version(schema):
    """
    Find the latest of the versions in the given schema.
    """
    latest_version_built_date = None
    latest_version = None
    for this_version in schema:
        this_version_built_date = parse_iso8601(this_version['built'])
        if (
            latest_version_built_date is None or
            this_version_built_date > latest_version_built_date
        ):
            latest_version_built_date = this_version_built_date
            latest_version = this_version
    return (latest_version_built_date, latest_version)


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
    with (open(filename, "wb")) as outfh:
        req = requests.get(url, timeout=HTTP_TIMEOUT_MAX)
        req.raise_for_status()
        outfh.write(req.content)


def download_version(version, output_dir):
    """
    Download a specific version of a vulnerability db.
    """
    filename = os.path.join(
        output_dir,
        version['url'].rsplit('/', 1)[-1]
    )
    download(version['url'], filename)


def download_dbs(listing, output_dir):
    """
    Optionally, download all, or only the latest, vulnerability database(s).
    """
    if output_dir:
        for schema in listing['available'].values():
            for version in schema:
                download_version(version, output_dir)
    else:
        logging.info("Refraining from downloading database.")


def output_listing_json(
    file_name, listing
):
    """
    Output a Grype style listing.json file.
    """
    logging.info(
        "Outputting listing.json to '%s'.",
        file_name
    )
    if file_name:
        with magic_open(file_name, "w") as output_file:
            print(json.dumps(listing), file=output_file)
    else:
        logging.info("Refraining from outputting new listing.json.")


def minimise_listing(listing):
    """
    Minimise a listing.json, so it contains only the latest database schema,
    and only the latest vulnerability database in that schema.
    """
    # Find the latest schema
    (latest_schema_key, latest_schema) = find_latest_schema(
        listing
    )
    logging.debug(
        "Latest schema: %s %s",
        latest_schema_key,
        latest_schema
    )
    # Find the latest version in the latest schema
    (
        latest_version_build_date,
        latest_version
    ) = find_latest_version(latest_schema)
    logging.info(
        "Latest version is %s",
        latest_version_build_date
    )
    listing['available'] = {
        latest_schema_key: [
            latest_version
        ]
    }
    return listing


def load_listing_json(input_url, minimal):
    """
    Load and parse a Grype style listing.json file.
    """
    with magic_open(input_url, "r") as input_file:
        listing = json.load(input_file)
        if minimal:
            minimise_listing(listing)
        return listing


def rewrite_urls(listing, new_prefix):
    """
    Replace the Anchore URL prefix on the given version's
    database URL with the given URL prefix.
    """
    if new_prefix:
        logging.debug(
            "Replacing '%s' with '%s' in database URLs",
            SRC_URL_PREFIX,
            new_prefix
        )
        for schema in listing['available'].values():
            for version in schema:
                new_url = version['url'].replace(
                    SRC_URL_PREFIX,
                    new_prefix
                )
                logging.debug(
                    "Updating URL from '%s' to '%s'",
                    version['url'],
                    new_url
                )
                version['url'] = new_url
    else:
        logging.info("Refraining from updating database URLs.")
