from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.request import Request

from ... import (
    mock,
    patch_service,
)

from reddit_service_ads_tracking.lib import (
    urls,
)


class UrlsTests(unittest.TestCase):
    def test_fix_query_encoding_does_not_change_query_order(self):
        url1 = "https://example.com?foo=bar&bar=foo"
        url2 = "https://example.com?bar=foo&foo=bar"

        self.assertEqual(urls.fix_query_encoding(url1), url1)
        self.assertEqual(urls.fix_query_encoding(url2), url2)

    def test_fix_query_encoding_multiple_of_the_same_key(self):
        url = "https://example.com?foo=1&foo=2&bar=far"

        self.assertEqual(urls.fix_query_encoding(url), url)

    def test_fix_query_encoding_retains_blank_values(self):
        url1 = "https://example.com?foo=&bar=bing"
        url2 = "https://example.com?foo="
        url3 = "https://example.com?bar=bing&foo="

        self.assertEqual(urls.fix_query_encoding(url1), url1)
        self.assertEqual(urls.fix_query_encoding(url2), url2)
        self.assertEqual(urls.fix_query_encoding(url3), url3)

    def test_fix_query_encoding_retains_blank_values_without_equals(self):
        url1 = "https://example.com?foo&bar=bing"
        url2 = "https://example.com?foo"
        url3 = "https://example.com?bar=bing&foo"

        self.assertEqual(urls.fix_query_encoding(url1), url1)
        self.assertEqual(urls.fix_query_encoding(url2), url2)
        self.assertEqual(urls.fix_query_encoding(url3), url3)

    def test_fix_query_encoding_encodes_values(self):
        url = "https://example.com?url=http://example.com&foo=bar"

        self.assertEqual(
            urls.fix_query_encoding(url),
            "https://example.com?url=http%3A%2F%2Fexample.com&foo=bar"
        )
