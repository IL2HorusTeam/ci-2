# coding: utf-8

from .views import WSParseView, http_get_data, http_health


def setup_routes(app):
    app.router.add_get(
        '/health', http_health,
    )
    app.router.add_get(
        '/data', http_get_data,
    )
    app.router.add_get(
        '/parse', WSParseView,
    )
