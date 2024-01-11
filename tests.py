#!/usr/bin/env python3


"""
Unit tests for the Listing module.
"""

import unittest
import json
# pylint: disable=no-name-in-module
from grype_cache.listing.listing import Listing
from grype_cache.server.httpserver import HttpServer
# pylint: enable=no-name-in-module


class TestListing(unittest.TestCase):

    """
    Test the Listing class.
    """

    @staticmethod
    def nuke_urls(*args):
        """
        Set all DB URLs the same, to ignore intended differences.
        """
        for data in args:
            for schema in data.values():
                for version in schema:
                    version['url'] = 'expected to differ'

    @staticmethod
    def load_json(filename):
        """
        Snarf a JSON file.
        """
        with open(
            filename,
            'r',
            encoding='utf-8'
        ) as filehandle:
            return json.load(filehandle)

    def test_roundtrip(self):
        """
        Test round-tripping the listing.
        """
        input_data = self.load_json("tests/input.json")
        actual_listing = Listing(input_data)
        with open(
            "tests/expected-output/roundtrip.json",
            "r",
            encoding='utf-8'
        ) as expected_output:
            expected_listing = json.load(expected_output)
            self.assertEqual(actual_listing.listing, expected_listing)

    def test_minimise(self):
        """
        Test minimising the listing.
        """
        input_data = self.load_json("tests/input.json")
        actual_listing = Listing(input_data)
        actual_listing.minimise()
        with open(
            "tests/expected-output/minimised.json",
            "r",
            encoding='utf-8'
        ) as expected_output:
            expected_listing = json.load(expected_output)
            self.assertEqual(
                actual_listing.listing['available']['5'][0],
                expected_listing['available']['5'][-1]
            )

    def test_rewrite(self):
        """
        Test rewriting the listing.
        """
        input_data = self.load_json("tests/input.json")
        actual_listing = Listing(input_data)
        actual_listing.rewrite_urls('http://example.com/')
        with open(
            "tests/expected-output/rewritten.json",
            "r",
            encoding='utf-8'
        ) as expected_output:
            expected_listing = json.load(expected_output)
            # The URLs are expected to differ, so we nuke them
            self.nuke_urls(
                actual_listing.listing['available'],
                expected_listing['available']
            )
            self.assertEqual(actual_listing.listing, expected_listing)

    def test_minimise_rewrite(self):
        """
        Test minimising and rewriting the listing.
        """
        input_data = self.load_json("tests/input.json")
        actual_listing = Listing(input_data)
        actual_listing.minimise()
        actual_listing.rewrite_urls('http://example.com/')
        with open(
            "tests/expected-output/minimised-rewritten.json",
            "r",
            encoding='utf-8'
        ) as expected_output:
            expected_listing = json.load(expected_output)
            # The URLs are expected to differ, so we nuke them
            self.nuke_urls(
                actual_listing.listing['available'],
                expected_listing['available']
            )
            self.assertEqual(
                actual_listing.listing['available']['5'][0],
                expected_listing['available']['5'][-1]
            )


class TestServer(unittest.TestCase):

    """
    Test the HttpServer class.
    """

    def setUp(self):
        """
        Set up the test by creating an HttpServer instance.
        """
        self.server = HttpServer(__name__)
        self.ctx = self.server.app_context()
        self.ctx.push()
        self.client = self.server.test_client()

    def tearDown(self):
        """
        Tear down the test.
        """
        self.ctx.pop()

    def test_listing_json(self):
        """
        Test reading the listing.json catalogue.
        """
        listing_response = self.client.get(
            self.server.public_listing_url().geturl()
        )
        self.assertEqual(listing_response.status_code, 200)
        listing_json = json.loads(listing_response.text)
        for schema in listing_json['available'].values():
            for version in schema:
                db_url = version['url']
                db_response = self.client.get(db_url)
                self.assertEqual(db_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
