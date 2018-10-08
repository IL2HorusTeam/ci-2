import os

from functools import wraps

from demo_services.core.response import RESTSuccess


CORS_ALLOW_ORIGIN_ENV_VAR_NAME = 'CORS_ALLOW_ORIGIN'


def make_headers(
    allow_origin=None,
    allow_methods=None,
    allow_headers=None,
    max_age=None,
):
    results = []

    if allow_origin is None:
        allow_origin = os.environ.get(CORS_ALLOW_ORIGIN_ENV_VAR_NAME)

    if allow_origin is not None:
        results.append(('Access-Control-Allow-Origin', allow_origin, ))

    if allow_methods is not None:
        allow_methods = ','.join(allow_methods)
        results.append(('Access-Control-Allow-Methods', allow_methods, ))

    if allow_headers is not None:
        results.append(('Access-Control-Allow-Headers', allow_headers, ))

    if max_age is not None:
        results.append(('Access-Control-Max-Age', max_age, ))

    return results


def with_cors(
    allow_origin=None,
    allow_methods=None,
    allow_headers=None,
    max_age=None,
):
    headers = make_headers(
        allow_origin=allow_origin,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        max_age=max_age,
    )

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method == 'OPTIONS':
                response = RESTSuccess()
            else:
                response = view_func(request, *args, **kwargs)

            for header, value in headers:
                response.headers.add(header, value)

            return response

        return wrapper

    return decorator
