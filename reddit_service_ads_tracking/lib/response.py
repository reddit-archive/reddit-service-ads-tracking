from pyramid.httpexceptions import HTTPMovedPermanently


def abort(request, status, message=None):
    request.response.status_int = status

    resp = {
        "status": status,
    }

    if message is not None:
        resp["reason"] = message

    return resp


def redirect(destination):
    return HTTPMovedPermanently(location=destination)
