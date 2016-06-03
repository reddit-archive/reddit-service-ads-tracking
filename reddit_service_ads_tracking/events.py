import baseplate.events
import logging

from urllib import unquote
from urlparse import urlparse

from reddit_service_ads_tracking.lib import useragent

logger = logging.getLogger(__name__)


def _get_domain(url):
    return urlparse(url).netloc


class EventQueue(baseplate.events.EventQueue):
    def put(self, event, request=None):
        try:
            super(EventQueue, self).put(event)
        except baseplate.events.EventTooLargeError as exc:
            logger.warning("%s", exc)

            if request:
                request.metrics.counter(
                    "eventcollector.oversize_dropped").increment()
        except baseplate.events.EventQueueFullError as exc:
            logger.warning("%s", exc)

            if request:
                request.metrics.counter(
                    "eventcollector.queue_full").increment()


class Event(baseplate.events.Event):
    def __init__(self, topic, event_type,
                 time=None, uuid=None, request=None):
        """Create a new event for event-collector.

        topic: Used to filter events into appropriate streams for processing
        event_type: Used for grouping and sub-categorizing events
        time: Should be a datetime.datetime object in UTC timezone
        uuid: Should be a UUID object
        request: A pylons.request object
        data: A dict of field names/values to initialize the payload with
        obfuscated_data: Same as `data`, but fields that need obfuscation
        """

        super(Event, self).__init__(
            topic=topic,
            event_type="ss.%s" % event_type,
            timestamp=time,
            id=uuid,
        )

        # this happens before we ingest data/obfuscated_data so explicitly
        # passed data can override the general context data
        if request is not None:
            request_data = self.get_request_data(request)
            for key, value in request_data.iteritems():
                self.set_field(key, value)

            sensitive_data = self.get_sensitive_request_data(request)
            for key, value in sensitive_data.iteritems():
                self.set_field(key, value, obfuscate=True)

    @classmethod
    def get_request_data(cls, request):
        """Extract common data from the current request

        request: A `pylons.request` object
        """
        data = {}
        cookies = request.cookies

        try:
            session_str = unquote(cookies.get("reddit_session", ""))
            user_id = int(session_str.split(",")[0])
        except ValueError:
            user_id = None

        if user_id:
            data["user_id"] = user_id
        else:
            data["loid"] = cookies.get("loid", None)
            data["loid_created"] = cookies.get("loidcreated", None)

        data["domain"] = request.host
        data["user_agent"] = request.user_agent
        data["user_agent_parsed"] = useragent.parse(request.user_agent)

        http_referrer = request.headers.get("Referer", None)
        if http_referrer:
            data["referrer_url"] = http_referrer
            data["referrer_domain"] = _get_domain(http_referrer)

        return data

    @classmethod
    def get_sensitive_request_data(cls, request):
        data = {}
        ip = getattr(request, "ip", None)
        if ip:
            data["client_ip"] = ip

        return data


class ClickEvent(Event):
    def __init__(self, url,
                 process_notes,
                 expired_on=None,
                 request=None,
                 **kwargs):
        super(ClickEvent, self).__init__(
            topic="ad_serving_event",
            event_type="ad_click",
            request=request,
        )

        self.set_field("url", url)
        self.set_field("process_notes", process_notes.value)
        self.set_field("expired_on", expired_on)

        for key, value in kwargs.items():
            self.set_field(key, value)
