from __future__ import absolute_import
from __future__ import unicode_literals

import base64
import json
import unittest
import urllib
import webtest

from baseplate.crypto import MessageSigner
from datetime import timedelta
from functools import partial
from pyramid.paster import get_appsettings

from .. import (
    mock,
    patch_service,
)

from reddit_service_ads_tracking import (
    config,
    make_wsgi_app,
)
from reddit_service_ads_tracking.lib import (
    response,
)


app_config = get_appsettings("example.ini", name="main")
cfg = config.parse_config(app_config)
signer = MessageSigner(cfg.ads_tracking.click_secret)


def _encode_data(data):
    return base64.urlsafe_b64encode(json.dumps(data))


def _generate_click_url(url, data, expires=None):
    if expires is None:
        expires = cfg.ads_tracking.max_click_age

    params = {
        "url": url,
        "data": data,
        "hmac": signer.make_signature(
            "|".join([url, data]),
            max_age=expires,
        ),
    }

    return "/click?%s" % urllib.urlencode(params)


class EndpointTests(unittest.TestCase):
    # ensure `MessageQueue`s aren't created since POSIX queues
    # don't play nice with the testing environment.
    @patch_service("events.EventQueue")
    def setUp(self, EventQueue):
        app = make_wsgi_app(app_config)
        self.test_app = webtest.TestApp(app)

    def test_health(self):
        response = self.test_app.get("/health")

        self.assertEqual(response.status_int, 200)

    def test_click_with_no_params(self):
        response = self.test_app.get("/click", status=400)

        self.assertResponse(
            response=response,
            status_int=400,
            content_type="application/json",
            body=dict(
                reason=partial(self.assertIn, "required"),
            )
        )

    def test_click_with_invalid_b64_data(self):
        response = self.test_app.get(
            _generate_click_url("https://example.com", "invalidbase64"),
            status=400,
        )

        self.assertResponse(
            response=response,
            status_int=400,
            content_type="application/json",
            body=dict(
                reason=partial(
                    self.assertStartsWith,
                    expected="unable to parse `data`",
                ),
            )
        )

    def test_click_with_invalid_json_data(self):
        response = self.test_app.get(
            _generate_click_url("https://example.com",
                                base64.b64encode("invalidjson")),
            status=400,
        )

        self.assertResponse(
            response=response,
            status_int=400,
            content_type="application/json",
            body=dict(
                reason=partial(
                    self.assertStartsWith,
                    expected="unable to parse `data`",
                ),
            )
        )

    def test_click_with_invalid_hmac(self):
        params = {
            "url": "https://example.com",
            "data": _encode_data({
                "link_id": "foo",
                "campaign_id": "bar",
            }),
            "hmac": "invalidhmac",
        }
        response = self.test_app.get(
            "/click?%s" % urllib.urlencode(params),
            status=403,
        )

        self.assertResponse(
            response=response,
            status_int=403,
            content_type="application/json",
        )

    def test_click_with_expired_hmac(self):
        url = "https://example.com"
        data = _encode_data({
            "link_id": "foo",
            "campaign_id": "bar",
        })

        click_url = _generate_click_url(
            url, data,
            expires=timedelta(seconds=-1),
        )
        response = self.test_app.get(
            click_url,
            status=302,
        )

        self.assertResponse(
            response=response,
            status_int=302,
            headers=dict(
                location=url,
            ),
        )

    def test_click_redirects(self):
        url = "https://example.com"
        data = _encode_data({
            "link_id": "foo",
            "campaign_id": "bar",
        })
        response = self.test_app.get(
            _generate_click_url(url, data),
            status=302,
        )

        self.assertResponse(
            response=response,
            status_int=302,
            headers=dict(
                location=url,
            )
        )

    def test_click_redirect_does_not_modify_query_params_order(self):
        url1 = "https://example.com?foo=bar&bar=foo"
        url2 = "https://example.com?bar=foo&foo=bar"
        data1 = _encode_data({
            "link_id": "foo",
            "campaign_id": "bar",
        })
        data2 = _encode_data({
            "link_id": "foo",
            "campaign_id": "bar",
        })
        response1 = self.test_app.get(
            _generate_click_url(url1, data1),
            status=302,
        )
        response2 = self.test_app.get(
            _generate_click_url(url2, data2),
            status=302,
        )

        self.assertResponse(
            response=response1,
            status_int=302,
            headers=dict(
                location=url1,
            )
        )
        self.assertResponse(
            response=response2,
            status_int=302,
            headers=dict(
                location=url2,
            )
        )

    def test_click_redirect_does_not_mangle_intermediate_redirects(self):
        url = "http://example.com?url=http%3A%2F%2Fexample.com"
        data = _encode_data({
            "link_id": "foo",
            "campaign_id": "bar",
        })
        response = self.test_app.get(
            _generate_click_url(url, data),
            status=302,
        )

        self.assertResponse(
            response=response,
            status_int=302,
            headers=dict(
                location=url,
            )
        )

    def assertStartsWith(self, actual, expected):
        self.assertTrue(actual.startswith(expected))

    def assertResponse(
        self, response, status_int,
        content_type=None,
        headers=None,
        body=None,
    ):
        self.assertEqual(response.status_int, status_int)

        if content_type is not None:
            self.assertEqual(response.content_type,
                             "application/json")

        if (response.content_type == "application/json"
                and isinstance(body, dict)):
            response_json = json.loads(response.body)

            for key, expected in body.items():
                actual = response_json[key]
                if callable(expected):
                    expected(actual)
                else:
                    self.assertEqual(actual, expected)
        elif body is not None:
            self.assertEqual(response.body, body)

        if isinstance(headers, dict):
            for key, expected in headers.items():
                actual = response.headers.get(key, None)
                if callable(expected):
                    expected(actual)
                else:
                    self.assertEqual(actual, expected)
        elif headers is not None:
            self.assertEqual(response.headers, headers)
