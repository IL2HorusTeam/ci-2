# coding: utf-8

from project.app import app

from .response.rest import (
    RESTBadRequest, RESTNotFound, RESTInternalServerError,
)


__all__ = (
    'bad_request_handler', 'not_found_handler',
    'internal_server_error_handler',
)


@app.errorhandler(400)
def bad_request_handler(error):
    return RESTBadRequest()


@app.errorhandler(404)
def not_found_handler(error):
    return RESTNotFound()


@app.errorhandler(Exception)
def internal_server_error_handler(error):
    return RESTInternalServerError()
