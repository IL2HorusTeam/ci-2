import configparser
import io
import logging

from il2fb.config.ds import ServerConfig

from demo_services.core import json
from demo_services.core.cors import with_cors
from demo_services.core.response import RESTSuccess, RESTBadRequest
from demo_services.core.response import RESTUnsupportedMediaType
from demo_services.core.validators import validate_upload

from demo_services.ds_config.constants import ALLOWED_EXTENSIONS
from demo_services.ds_config.constants import ALLOWED_CONTENT_TYPES


LOG = logging.getLogger(__name__)


@with_cors(
    allow_methods=('GET', 'OPTIONS'),
)
def get_defaults(request):
    pretty = 'pretty' in request.args
    payload = {
        'data': ServerConfig.default().to_primitive(),
    }
    return RESTSuccess(payload, pretty=pretty)


@with_cors(
    allow_methods=('POST', 'OPTIONS'),
)
def parse(request):
    pretty = 'pretty' in request.args

    try:
        storage = request.files['file']
    except Exception as e:
        LOG.exception("failed to upload config")
        return RESTBadRequest(
            detail=f"Failed to upload config: {e}",
            pretty=pretty,
        )

    try:
        validate_upload(
            storage.filename,
            storage.content_type,
            ALLOWED_EXTENSIONS,
            ALLOWED_CONTENT_TYPES,
        )
    except ValueError as e:
        LOG.error(
            f"uploaded config '{storage.filename}' is invalid: {e}"
        )
        return RESTBadRequest(
            detail=f"Uploaded config is invalid: {e}",
            pretty=pretty,
        )

    try:
        content = storage.read().decode()
        ini = configparser.ConfigParser()
        ini.read_string(content)
    except Exception as e:
        LOG.exception(
            f"failed to read config '{storage.filename}'"
        )
        return RESTBadRequest(
            detail=f"Failed to read config: {e}",
            pretty=pretty,
        )

    try:
        data = ServerConfig.from_ini(ini).to_primitive()
    except Exception:
        LOG.exception(
            f"failed to parse config '{storage.filename}'"
        )
        return RESTBadRequest(
            detail=f"Failed to parse config '{storage.filename}'",
            pretty=pretty,
        )

    if not data:
        return RESTBadRequest(
            detail=(
                "Config is blank or does not contain any known sections"
            ),
            pretty=pretty,
        )

    return RESTSuccess(
        payload={
            'file_name': storage.filename,
            'data': data,
        },
        pretty=pretty,
    )


@with_cors(
    allow_methods=('POST', 'OPTIONS'),
    allow_headers='Content-Type',
)
def compose(request):
    pretty = 'pretty' in request.args

    if not request.is_json:
        LOG.error(
            f"failed to compose config: invalid content type "
            f"'{request.content_type}'"
        )
        return RESTUnsupportedMediaType(
            detail=f"Failed to compose config: invalid content type",
            pretty=pretty,
        )

    try:
        content = json.loads(request.data.decode())
    except Exception as e:
        LOG.exception("failed to compose config")
        return RESTBadRequest(
            detail=f"Failed to compose config: {e}",
            pretty=pretty,
        )

    try:
        ini = configparser.ConfigParser()
        ini.optionxform = str
        ServerConfig.from_flat(content).to_ini(ini)
    except Exception as e:
        LOG.exception("failed to compose config")
        return RESTBadRequest(
            detail=f"Failed to compose config: {e}",
            pretty=pretty,
        )

    try:
        f = io.StringIO()
        ini.write(f, space_around_delimiters=False)
        data = f.getvalue()
    except Exception as e:
        LOG.exception("failed to dump config")
        return RESTBadRequest(
            detail=f"Failed to compose config: {e}",
            pretty=pretty,
        )

    return RESTSuccess(
        payload={
            'data': data,
        },
        pretty=pretty,
    )
