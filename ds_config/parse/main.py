import configparser
import logging
import os

from functools import partial
from functools import wraps

from flask import Response
from il2fb.config.ds import ServerConfig
from itsdangerous import json as _json


_demo_services_ds_config_views_LOG = logging.getLogger(__name__)


_demo_services_ds_config_constants_ALLOWED_EXTENSIONS = {'ini'}


_demo_services_ds_config_constants_ALLOWED_CONTENT_TYPES = {'application/octet-stream'}


def _demo_services_core_validators_validate_upload(
    file_name,
    content_type,
    allowed_extensions,
    allowed_content_types,
):
    if (
        '.' not in file_name
        or file_name.rsplit('.', 1)[1] not in allowed_extensions
        or content_type not in allowed_content_types
    ):
        raise ValueError("file type is not supported")


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


class _demo_services_core_response_RESTBadRequest(_demo_services_core_response_RESTResponse):
    code = 400
    detail = "Bad request"


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
)
def parse(request):
    pretty = 'pretty' in request.args

    try:
        storage = request.files['file']
    except Exception as e:
        _demo_services_ds_config_views_LOG.exception("failed to upload config")
        return _demo_services_core_response_RESTBadRequest(
            detail=f"Failed to upload config: {e}",
            pretty=pretty,
        )

    try:
        _demo_services_core_validators_validate_upload(
            storage.filename,
            storage.content_type,
            _demo_services_ds_config_constants_ALLOWED_EXTENSIONS,
            _demo_services_ds_config_constants_ALLOWED_CONTENT_TYPES,
        )
    except ValueError as e:
        _demo_services_ds_config_views_LOG.error(
            f"uploaded config '{storage.filename}' is invalid: {e}"
        )
        return _demo_services_core_response_RESTBadRequest(
            detail=f"Uploaded config is invalid: {e}",
            pretty=pretty,
        )

    try:
        content = storage.read().decode()
        ini = configparser.ConfigParser()
        ini.read_string(content)
    except Exception as e:
        _demo_services_ds_config_views_LOG.exception(
            f"failed to read config '{storage.filename}'"
        )
        return _demo_services_core_response_RESTBadRequest(
            detail=f"Failed to read config: {e}",
            pretty=pretty,
        )

    try:
        data = ServerConfig.from_ini(ini).to_primitive()
    except Exception:
        _demo_services_ds_config_views_LOG.exception(
            f"failed to parse config '{storage.filename}'"
        )
        return _demo_services_core_response_RESTBadRequest(
            detail=f"Failed to parse config '{storage.filename}'",
            pretty=pretty,
        )

    if not data:
        return _demo_services_core_response_RESTBadRequest(
            detail=(
                "Config is blank or does not contain any known sections"
            ),
            pretty=pretty,
        )

    return _demo_services_core_response_RESTSuccess(
        payload={
            'file_name': storage.filename,
            'data': data,
        },
        pretty=pretty,
    )


