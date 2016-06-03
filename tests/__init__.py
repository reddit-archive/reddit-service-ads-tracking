try:
    from unittest import mock
except ImportError:
    import mock


def patch_service(*args, **kwargs):
    path = args[0]
    return mock.patch("reddit_service_ads_tracking.%s" % path, *args[1:], **kwargs)


__all__ = [
    "mock",
    "patch_service"
]
