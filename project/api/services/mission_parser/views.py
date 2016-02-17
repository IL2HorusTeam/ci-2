# -*- coding: utf-8 -*-

from project.app import app
from project.api.response.rest import RESTSuccess


__all__ = ('parse', )


def api_route(path, *args, **kwargs):
    return app.route("/api/v1/mission-parser/{0}".format(path), *args, **kwargs)


@api_route('parse', methods=['POST'])
def parse():
    return RESTSuccess(detail="hello!")
