from flask import Response

from demo_services.core import json


class RESTResponse(Response):
    separators = (',', ':')

    code = None
    detail = None

    def __init__(self, payload=None, detail=None, pretty=False, **kwargs):
        if payload is None:
            payload = {}

        if detail is None:
            detail = self.detail

        if detail:
            payload['detail'] = str(detail)

        indent = 2 if pretty else None

        # Add '\n' to end of response
        # (see https://github.com/mitsuhiko/flask/pull/1262)
        response = json.dumps(payload, indent=indent) + '\n'

        kwargs.setdefault('status', self.code)
        kwargs['mimetype'] = 'application/json'

        super().__init__(response, **kwargs)


class RESTSuccess(RESTResponse):
    code = 200


class RESTBadRequest(RESTResponse):
    code = 400
    detail = "Bad request"


class RESTNotFound(RESTBadRequest):
    code = 404
    detail = "Resource not found"


class RESTNotAllowed(RESTBadRequest):
    code = 405
    detail = "Method not allowed"


class RESTConflict(RESTBadRequest):
    code = 409
    detail = "Conflict"


class RESTUnsupportedMediaType(RESTBadRequest):
    code = 415
    detail = "Unsupported media type"


class RESTInternalServerError(RESTResponse):
    code = 500
    detail = "Service has crashed"
