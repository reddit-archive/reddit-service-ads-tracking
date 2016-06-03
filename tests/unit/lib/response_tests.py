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
    response,
)


class ResponseTests(unittest.TestCase):
    def setUp(self):
        self.request = mock.MagicMock(autospec=Request)

    def test_abort(self):
        result = response.abort(self.request, 400)

        self.assertEqual(self.request.response.status_int, 400)
        self.assertEqual(result, {
            "status": 400,
        })

    def test_abort_message(self):
        result = response.abort(self.request, 403, "not allowed")

        self.assertEqual(self.request.response.status_int, 403)
        self.assertEqual(result, {
            "status": 403,
            "reason": "not allowed",
        })

    def test_redirect(self):
        url = "https://example.com"
        result = response.redirect(url)

        self.assertIsInstance(result, HTTPMovedPermanently)
        self.assertEqual(result.location, url)
