import urllib

from urlparse import (
    urlparse,
)


def _encode_query(query):
    """
    `urlparse.parse_qsl` and `urllib.encodeurl` modify
    blank query values so we had to roll our own.
    """
    kvps = urllib.unquote_plus(query).split("&")
    encoded_pairs = []

    for kvp in kvps:
        if "=" not in kvp:
            encoded_pairs.append(urllib.quote_plus(kvp))
        else:
            key, value = kvp.split("=")
            encoded_pairs.append("%s=%s" % (
                urllib.quote_plus(key),
                urllib.quote_plus(value)
            ))

    return "&".join(encoded_pairs)



def fix_query_encoding(url):
    "Fix encoding in the query string."

    parsed = urlparse(url)
    if parsed.query:
        # this effectively calls urllib.quote_plus on every query value
        parsed = parsed._replace(
            query=_encode_query(parsed.query)
        )

    return parsed.geturl()
