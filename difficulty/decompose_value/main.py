import os

from functools import partial
from functools import wraps
from itertools import chain

from flask import Response
from il2fb.config.difficulty import autocorrect_difficulty
from il2fb.config.difficulty import decompose
from il2fb.config.difficulty import get_actual_rules
from il2fb.config.difficulty.constants import RULE_TYPES
from itsdangerous import json as _json


class _demo_services_core_json_JSONEncoder(_json.JSONEncoder):

    def default(self, obj):
        if hasattr(obj, 'to_primitive'):
            result = obj.to_primitive()
        elif hasattr(obj, 'isoformat'):
            result = obj.isoformat()
        else:
            result = super().default(obj)

        return result


_demo_services_core_json_dumps = partial(_json.dumps, cls=_demo_services_core_json_JSONEncoder)


class _demo_services_core_response_RESTResponse(Response):
    separators = (',', ':')

    code = None
    detail = None

    def __init__(self, payload=None, detail=None, pretty=False, **kwargs):
        if payload is None:
            payload = {}

        if detail is None:
            detail = self.detail

        if detail:
            payload['detail'] = str(detail)

        indent = 2 if pretty else None

        # Add '\n' to end of response
        # (see https://github.com/mitsuhiko/flask/pull/1262)
        response = _demo_services_core_json_dumps(payload, indent=indent) + '\n'

        kwargs.setdefault('status', self.code)
        kwargs['mimetype'] = 'application/json'

        super().__init__(response, **kwargs)


class _demo_services_core_response_RESTSuccess(_demo_services_core_response_RESTResponse):
    code = 200


_demo_services_core_cors_CORS_ALLOW_ORIGIN_ENV_VAR_NAME = """CORS_ALLOW_ORIGIN"""


def _demo_services_core_cors_make_headers(
    allow_origin=None,
    allow_methods=None,
    allow_headers=None,
    max_age=None,
):
    results = []

    if allow_origin is None:
        allow_origin = os.environ.get(_demo_services_core_cors_CORS_ALLOW_ORIGIN_ENV_VAR_NAME)

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


def _demo_services_core_cors_with_cors(
    allow_origin=None,
    allow_methods=None,
    allow_headers=None,
    max_age=None,
):
    headers = _demo_services_core_cors_make_headers(
        allow_origin=allow_origin,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        max_age=max_age,
    )

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method == 'OPTIONS':
                response = _demo_services_core_response_RESTSuccess()
            else:
                response = view_func(request, *args, **kwargs)

            for header, value in headers:
                response.headers.add(header, value)

            return response

        return wrapper

    return decorator


@_demo_services_core_cors_with_cors(
    allow_methods=('POST', 'OPTIONS'),
    allow_headers='Content-Type',
)
def decompose_value(request):
    pretty = 'pretty' in request.args
    body = request.get_json()

    difficulty = int(body['difficulty'])
    difficulty, _ = autocorrect_difficulty(difficulty)

    actual_rules = get_actual_rules(difficulty).values()
    locked = [
        rules[RULE_TYPES.LOCKS]
        for rules in actual_rules
        if RULE_TYPES.LOCKS in rules
    ]
    locked = [
        parameter.value
        for parameter in set(chain(*locked))
    ]

    parameters = {
        parameter.value: value
        for parameter, value in decompose(difficulty).items()
    }

    payload = {
        'difficulty': difficulty,
        'locked': locked,
        'parameters': parameters,
    }

    return _demo_services_core_response_RESTSuccess(payload, pretty=pretty)


