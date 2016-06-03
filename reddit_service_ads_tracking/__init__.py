import base64
import logging
import json
import time

from baseplate import (
    Baseplate,
    make_metrics_client,
)
from baseplate.crypto import (
    ExpiredSignatureError,
    IncorrectSignatureError,
    MessageSigner,
    UnreadableSignatureError,
)
from baseplate.integration.pyramid import BaseplateConfigurator
from enum import Enum
from pyramid.config import Configurator

from reddit_service_ads_tracking import (
    config,
    events,
)
from reddit_service_ads_tracking.lib import (
    response,
    urls,
)


logger = logging.getLogger(__name__)


class ClickProcessNotes(Enum):
    VALID = "VALID"
    EXPIRED_SIGNATURE = "EXPIRED_SIGNATURE"
    INVALID_SIGNATURE = "INVALID_SIGNATURE"
    BAD_DATA = "BAD_DATA"


class TrackingService(object):
    def __init__(self, signer):
        self.signer = signer

    def is_healthy(self, request):
        return {
            "status": "healthy",
        }

    def track_conversion(self, request):
        pass

    def track_impression(self, request):
        pass

    def track_click(self, ctx):
        url = ctx.GET.get("url", "").encode("utf-8")
        b64_data = ctx.GET.get("data", "").encode("utf-8")
        observed_mac = ctx.GET.get("hmac", "").encode("utf-8")

        if (not url or
                not b64_data or
                not observed_mac):
            return response.abort(ctx, 400,
                                  "missing required query parameters")

        result = None
        process_notes = ClickProcessNotes.VALID
        expired_on = None

        try:
            self.signer.validate_signature(
                "|".join([url, b64_data]), observed_mac)

            ctx.metrics.counter("click.signature.success").increment()
        except ExpiredSignatureError as e:
            ctx.metrics.counter("click.signature.expired").increment()
            process_notes = ClickProcessNotes.EXPIRED_SIGNATURE
            expired_on = e.expiration
        except (UnreadableSignatureError, IncorrectSignatureError):
            ctx.metrics.counter("click.signature.error").increment()
            process_notes = ClickProcessNotes.INVALID_SIGNATURE
            result = response.abort(ctx, 403)

        data = {}

        try:
            json_string = base64.urlsafe_b64decode(b64_data)
            data = json.loads(json_string)
        except (TypeError, ValueError) as e:
            ctx.metrics.counter("click.data.parse_error").increment()
            process_notes = ClickProcessNotes.BAD_DATA
            result = response.abort(ctx, 400,
                                    "unable to parse `data`: %s" % e.message)

        destination = urls.fix_query_encoding(url)
        click = events.ClickEvent(
            url=destination,
            process_notes=process_notes,
            ctx=ctx,
            expired_on=expired_on,
            **data
        )

        ctx.events.put(click)

        if result:
            return result

        return response.redirect(destination)


def make_wsgi_app(app_config):
    cfg = config.parse_config(app_config)
    signer = MessageSigner(cfg.ads_tracking.click_secret)

    metrics_client = make_metrics_client(app_config)

    baseplate = Baseplate()
    baseplate.configure_logging()
    baseplate.configure_metrics(metrics_client)
    baseplate.add_to_context("events", events.EventQueue("production"))
    baseplate.add_to_context("events_test", events.EventQueue("test"))

    configurator = Configurator(settings=app_config)

    baseplate_configurator = BaseplateConfigurator(baseplate)
    configurator.include(baseplate_configurator.includeme)

    controller = TrackingService(
        signer=signer,
    )
    configurator.add_route("health", "/health", request_method="GET")
    configurator.add_view(
        controller.is_healthy, route_name="health", renderer="json")

    configurator.add_route("click", "/click", request_method="GET")
    configurator.add_view(
        controller.track_click, route_name="click", renderer="json")

    return configurator.make_wsgi_app()
