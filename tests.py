#!/usr/bin/env python3


"""
Unit tests for the Listing module.
"""

import unittest
import json
from listing import Listing


class TestListing(unittest.TestCase):

    """
    Test the Listing class.
    """

    @staticmethod
    def nuke_urls(*args):
        for data in args:
            for schema in data.values():
                for version in schema:
                    version['url'] = 'expected to differ'

    def test_roundtrip(self):
        """
        Test round-tripping the listing.
        """
        actual_listing = Listing("tests/input.json", False)
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
        actual_listing = Listing("tests/input.json", True)
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
        actual_listing = Listing("tests/input.json", False)
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
        actual_listing = Listing("tests/input.json", True)
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


if __name__ == "__main__":
    unittest.main()
