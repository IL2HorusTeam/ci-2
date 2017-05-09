# coding: utf-8

from .views import ParseView, http_health


def setup_routes(app):
    app.router.add_get(
        '/health', http_health,
    )
    app.router.add_post(
        '/parse', ParseView,
    )
