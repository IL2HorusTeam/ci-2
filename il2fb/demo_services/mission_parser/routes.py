# coding: utf-8

from .views import ParseView


def setup_routes(app):
    app.router.add_post(
        '/parse', ParseView,
    )
