from __future__ import absolute_import
from __future__ import unicode_literals

import json
import unittest

from baseplate.events import (
    EventQueue,
    EventQueueFullError,
    EventTooLargeError,
    MAX_EVENT_SIZE,
)
from pyramid.request import Request

from .. import (
    mock,
    patch_service,
)

from reddit_service_ads_tracking import (
    ClickProcessNotes,
    events,
)
from reddit_service_ads_tracking.lib import (
    useragent,
)

IP_V4 = "192.168.1.1"
IP_V6 = "2001:0db8:0a0b:12f0:0000:0000:0000:0001"
USER_ID = 99999
REDDIT_SESSION = "%d,2016-06-15T11:17:12,abcd12345" % USER_ID
LOID = "FlFS2kMsdssc1Cyen"
LOID_CREATED = "2016-06-14T19:20:59.072Z"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)"
    " AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/50.0.2661.102 Safari/537.36"
)

USER_AGENT_PARSED = useragent.parse(USER_AGENT)


class EventQueueTests(unittest.TestCase):
    @patch_service("events.EventQueue.__init__")
    def setUp(self, __init__):
        # ensure `MessageQueues` aren't created since POSIX queues
        # don't play nice with the testing environment.
        __init__.return_value = None

        self.queue = events.EventQueue("test")

    def test_put(self):
        mock_event = mock.MagicMock(autospec=events.Event)

        with patch_service("events.baseplate.events.EventQueue.put") as put:
            self.queue.put(mock_event)

            self.assertEqual(put.call_count, 1)
            args, kwargs = put.call_args
            self.assertEqual(args[0], mock_event)

    @patch_service("events.logger")
    def test_put_too_large(self, logger):
        mock_event = mock.MagicMock(autospec=events.Event)
        mock_metrics = mock.MagicMock()

        with patch_service("events.baseplate.events.EventQueue.put") as put:
            put.side_effect = EventTooLargeError(MAX_EVENT_SIZE + 1)

            self.queue.put(mock_event)
            self.assertEqual(logger.warning.call_count, 1)
            self.assertEqual(mock_metrics.counter.call_count, 0)

    @patch_service("events.logger")
    def test_put_too_large_with_request(self, logger):
        mock_event = mock.MagicMock(autospec=events.Event)
        mock_metrics = mock.MagicMock()
        mock_request = mock.MagicMock(
            metrics=mock_metrics,
            autospec=Request,
        )

        with patch_service("events.baseplate.events.EventQueue.put") as put:
            put.side_effect = EventTooLargeError(MAX_EVENT_SIZE + 1)

            self.queue.put(mock_event, mock_request)
            self.assertEqual(logger.warning.call_count, 1)
            self.assertEqual(mock_metrics.counter.call_count, 1)

    @patch_service("events.logger")
    def test_put_queue_full(self, logger):
        mock_event = mock.MagicMock(autospec=events.Event)
        mock_metrics = mock.MagicMock()

        with patch_service("events.baseplate.events.EventQueue.put") as put:
            put.side_effect = EventQueueFullError

            self.queue.put(mock_event)
            self.assertEqual(logger.warning.call_count, 1)
            self.assertEqual(mock_metrics.counter.call_count, 0)

    @patch_service("events.logger")
    def test_put_queue_full_with_request(self, logger):
        mock_event = mock.MagicMock(autospec=events.Event)
        mock_metrics = mock.MagicMock()
        mock_request = mock.MagicMock(
            metrics=mock_metrics,
            autospec=Request,
        )

        with patch_service("events.baseplate.events.EventQueue.put") as put:
            put.side_effect = EventQueueFullError

            self.queue.put(mock_event, mock_request)
            self.assertEqual(logger.warning.call_count, 1)
            self.assertEqual(mock_metrics.counter.call_count, 1)


class EventTests(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 1000000

    def test_constructor(self):
        event = events.Event(
            topic="test",
            event_type="foo",
        )

        self.assertEqual(event.topic, "test")
        self.assertEqual(event.event_type, "ss.foo")

    @mock.patch("uuid.uuid4")
    @mock.patch("time.time")
    def test_constructor_with_request(self, time, uuid):
        time.return_value = 333
        uuid.return_value = "1-2-3-4"

        mock_request = mock.MagicMock(
            ip=IP_V4,
            cookies={
                "loid": LOID,
                "loidcreated": LOID_CREATED,
            },
            headers={
                "Referer": "https://reddit.com/r/test"
            },
            host="reddit.com",
            user_agent=USER_AGENT,
            autospec=Request,
        )

        event = events.Event(
            topic="test",
            event_type="foo",
            request=mock_request,
        )

        self.assertEqual(json.loads(event.serialize()), {
            "event_topic": "test",
            "event_type": "ss.foo",
            "event_ts": 333000,
            "uuid": "1-2-3-4",
            "payload": {
                "loid": LOID,
                "loid_created": LOID_CREATED,
                "domain": "reddit.com",
                "user_agent": USER_AGENT,
                "user_agent_parsed": USER_AGENT_PARSED,
                "referrer_url": "https://reddit.com/r/test",
                "referrer_domain": "reddit.com",
                "obfuscated_data": {
                    "client_ip": IP_V4,
                },
            },
        })

    def test_get_request_data_logged_out(self):
        mock_request = mock.MagicMock(
            cookies={
                "loid": LOID,
                "loidcreated": LOID_CREATED,
            },
            headers={
                "Referer": "https://reddit.com/r/test"
            },
            host="reddit.com",
            user_agent=USER_AGENT,
            autospec=Request,
        )

        data = events.Event.get_request_data(mock_request)

        self.assertEqual(data, dict(
            loid=LOID,
            loid_created=LOID_CREATED,
            domain="reddit.com",
            user_agent=USER_AGENT,
            user_agent_parsed=USER_AGENT_PARSED,
            referrer_url="https://reddit.com/r/test",
            referrer_domain="reddit.com",
        ))

    def test_get_request_data_logged_in(self):
        mock_request = mock.MagicMock(
            cookies={
                "reddit_session": REDDIT_SESSION,
                "loid": LOID,
                "loidcreated": LOID_CREATED,
            },
            headers={
                "Referer": "https://reddit.com/r/test"
            },
            host="reddit.com",
            user_agent=USER_AGENT,
            autospec=Request,
        )

        data = events.Event.get_request_data(mock_request)

        self.assertEqual(data, dict(
            user_id=USER_ID,
            domain="reddit.com",
            user_agent=USER_AGENT,
            user_agent_parsed=USER_AGENT_PARSED,
            referrer_url="https://reddit.com/r/test",
            referrer_domain="reddit.com",
        ))

    def test_get_request_data_invalid_session(self):
        mock_request = mock.MagicMock(
            cookies={
                "reddit_session": "invalid",
                "loid": LOID,
                "loidcreated": LOID_CREATED,
            },
            headers={
                "Referer": "https://reddit.com/r/test"
            },
            host="reddit.com",
            user_agent=USER_AGENT,
            autospec=Request,
        )

        data = events.Event.get_request_data(mock_request)

        self.assertEqual(data, dict(
            loid=LOID,
            loid_created=LOID_CREATED,
            domain="reddit.com",
            user_agent=USER_AGENT,
            user_agent_parsed=USER_AGENT_PARSED,
            referrer_url="https://reddit.com/r/test",
            referrer_domain="reddit.com",
        ))

    def test_get_request_data_no_referrer(self):
        mock_request = mock.MagicMock(
            cookies={
                "reddit_session": REDDIT_SESSION,
                "loid": LOID,
                "loidcreated": LOID_CREATED,
            },
            headers={
                "Referer": ""
            },
            host="reddit.com",
            user_agent=USER_AGENT,
            autospec=Request,
        )

        data = events.Event.get_request_data(mock_request)

        self.assertEqual(data, dict(
            user_id=USER_ID,
            domain="reddit.com",
            user_agent=USER_AGENT,
            user_agent_parsed=USER_AGENT_PARSED,
        ))

    def test_get_sensitive_request_data_with_no_ip(self):
        mock_request = {}

        data = events.Event.get_sensitive_request_data(mock_request)

        self.assertEqual(data, {})

    def test_get_sensitive_request_data_with_ipv4(self):
        mock_request = mock.MagicMock(
            ip=IP_V4,
        )

        data = events.Event.get_sensitive_request_data(mock_request)

        self.assertEqual(data, dict(
            client_ip=IP_V4,
        ))

    def test_get_sensitive_request_data_with_ipv6(self):
        mock_request = mock.MagicMock(
            ip=IP_V6,
        )

        data = events.Event.get_sensitive_request_data(mock_request)

        self.assertEqual(data, dict(
            client_ip=IP_V6,
        ))


class ClickEventTests(unittest.TestCase):
    def test_minimal_constructor(self):
        click = events.ClickEvent(
            url="http://example.com",
            process_notes=ClickProcessNotes.VALID,
            foo="bar",
            boo="far",
        )

        self.assertEqual(click.topic, "ad_interaction_events")
        self.assertEqual(click.event_type, "ss.ad_click")
        self.assertEqual(click.get_field("url"), "http://example.com")
        self.assertEqual(click.get_field("process_notes"), "VALID")
        self.assertEqual(click.get_field("foo"), "bar")
        self.assertEqual(click.get_field("boo"), "far")
