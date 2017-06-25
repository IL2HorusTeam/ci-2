# coding: utf-8

from .views import DefaultView, ParseFileView, ComposeFileView, http_health


def setup_routes(app):
    app.router.add_get(
        '/health', http_health,
    )
    app.router.add_get(
        '/default', DefaultView,
    )
    app.router.add_post(
        '/file/parse', ParseFileView,
    )
    app.router.add_post(
        '/file/compose', ComposeFileView,
    )
