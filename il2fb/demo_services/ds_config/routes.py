# coding: utf-8

from .views import DefaultView, ParseFileView


def setup_routes(app):
    app.router.add_get(
        '/default', DefaultView,
    )
    app.router.add_get(
        '/parse/file', ParseFileView,
    )
