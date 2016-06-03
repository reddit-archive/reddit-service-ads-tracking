import urllib

from urlparse import (
    parse_qsl,
    urlparse,
    urlunparse,
)


def fix_query_encoding(url):
    "Fix encoding in the query string."

    parsed = urlparse(url)
    if parsed.query:
        query_params = parse_qsl(
            parsed.query,
            keep_blank_values=True,
        )

        # this effectively calls urllib.quote_plus on every query value
        parsed = parsed._replace(
            query=urllib.urlencode(query_params)
        )

    return parsed.geturl()
