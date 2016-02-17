# -*- coding: utf-8 -*-

import ujson as json
import six

from flask import Response, current_app, request


class RESTResponse(Response):
    indent = None
    separators = (',', ':')

    code = None
    detail = None

    def __init__(self, payload=None, detail=None, **kwargs):
        payload = payload or {}

        detail = detail or self.detail
        if detail:
            payload['detail'] = six.text_type(detail)

        if (
            current_app.config['JSONIFY_PRETTYPRINT_REGULAR']
            and not request.is_xhr
        ):
            indent = 2
        else:
            indent = kwargs.pop('indent', self.indent)

        # Note that we add '\n' to end of response
        # (see https://github.com/mitsuhiko/flask/pull/1262)
        response = (
            json.dumps(payload, indent),
            '\n',
        )

        kwargs.setdefault('status', self.code)
        kwargs['mimetype'] = 'application/json'

        super(RESTResponse, self).__init__(response, **kwargs)


class RESTSuccess(RESTResponse):
    code = 200


class RESTBadRequest(RESTResponse):
    code = 400
    detail = "Bad request."


class RESTNotFound(RESTBadRequest):
    code = 404
    detail = "Resource not found."


class RESTConflict(RESTBadRequest):
    code = 409
    detail = "Conflict."


class RESTInternalServerError(RESTResponse):
    code = 500
    detail = (
        "The server encountered an unexpected condition that prevented it "
        "from fulfilling the request.")
