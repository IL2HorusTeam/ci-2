from functools import wraps

from flask import request


def with_request(view_func):

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        return view_func(request, *args, **kwargs)

    return wrapper
