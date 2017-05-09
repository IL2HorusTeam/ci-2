# coding: utf-8

from .views import http_get_data, http_decompose_difficulty, http_health
from .views import http_toggle_parameter


def setup_routes(app):
    app.router.add_get(
        '/health', http_health,
    )
    app.router.add_get(
        '/data', http_get_data,
    )
    app.router.add_post(
        '/decompose', http_decompose_difficulty,
    )
    app.router.add_post(
        '/toggle_parameter', http_toggle_parameter,
    )
