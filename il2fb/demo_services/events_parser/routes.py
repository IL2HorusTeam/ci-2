# coding: utf-8

from .views import http_get_data, WSParseView


def setup_routes(app):
    app.router.add_get(
        '/data', http_get_data,
    )
    app.router.add_get(
        '/parse', WSParseView,
    )
