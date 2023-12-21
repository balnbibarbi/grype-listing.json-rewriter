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

    def test_minimise(self):
        """
        Test loading and minimising the listing.
        """
        actual_listing = Listing("tests/input.json", True)
        with open(
            "tests/expected-output.json",
            "r",
            encoding='utf-8'
        ) as expected_output:
            expected_listing = json.load(expected_output)
            # The URLs are expected to differ, so we nuke them
            for data in (
                actual_listing.listing['available'],
                expected_listing['available']
            ):
                for schema in data.values():
                    for version in schema:
                        version['url'] = 'expected to differ'
            self.assertEqual(actual_listing.listing, expected_listing)


if __name__ == "__main__":
    unittest.main()
