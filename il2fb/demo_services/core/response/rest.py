# coding: utf-8

import abc

import ujson as json

from aiohttp import web


class RESTResponse(web.Response, abc.ABC):
    detail = None

    @property
    @abc.abstractmethod
    def status(self):
        """
        Status must be explicilty defined by subclasses.

        """

    def __init__(
        self, payload=None, detail=None, pretty=False,
        content_type='application/json', charset='utf-8', **kwargs
    ):
        payload = payload or {}

        detail = detail or self.detail
        if detail:
            payload['detail'] = str(detail)

        indent = 2 if pretty else 0
        text = json.dumps(payload, indent=indent) + '\n'

        kwargs.setdefault('status', self.status)

        super().__init__(
            text=text,
            charset=charset,
            content_type=content_type,
            **kwargs
        )


class RESTSuccess(RESTResponse):
    status = 200


class RESTBadRequest(RESTResponse):
    status = 400
    detail = "Bad request."


class RESTNotFound(RESTBadRequest):
    status = 404
    detail = "Resource not found."


class RESTConflict(RESTBadRequest):
    status = 409
    detail = "Conflict."


class RESTInternalServerError(RESTResponse):
    status = 500
    detail = (
        "The server encountered an unexpected condition that prevented it "
        "from fulfilling the request."
    )
