import io
import logging

from il2fb.parsers.mission import MissionParser

from demo_services.core.cors import with_cors
from demo_services.core.response import RESTSuccess, RESTBadRequest
from demo_services.core.validators import validate_upload

from demo_services.mission_parser.constants import ALLOWED_EXTENSIONS
from demo_services.mission_parser.constants import ALLOWED_CONTENT_TYPES


LOG = logging.getLogger(__name__)
PARSER = MissionParser()


@with_cors(allow_methods=('POST', 'OPTIONS'))
def parse(request):
    pretty = 'pretty' in request.args

    try:
        storage = request.files['file']
    except Exception as e:
        LOG.exception("failed to upload mission")
        return RESTBadRequest(
            detail=f"Failed to upload mission: {e}",
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
            f"uploaded mission '{storage.filename}' is invalid: {e}"
        )
        return RESTBadRequest(
            detail=f"Uploaded mission is invalid: {e}",
            pretty=pretty,
        )

    try:
        content = storage.read().decode()
    except Exception as e:
        LOG.exception(
            f"failed to read mission '{storage.filename}'"
        )
        return RESTBadRequest(
            detail=f"Failed to read mission: {e}",
            pretty=pretty,
        )

    try:
        stream = io.StringIO(content)
        data = PARSER.parse(stream)
    except Exception:
        LOG.exception(
            f"failed to parse mission '{storage.filename}'"
        )
        return RESTBadRequest(
            detail=f"Failed to parse mission '{storage.filename}'",
            pretty=pretty,
        )

    if not data:
        return RESTBadRequest(
            detail="Mission is blank or does not contain any known sections",
            pretty=pretty,
        )

    return RESTSuccess(
        pretty=pretty,
        payload={
            'file_name': storage.filename,
            'data': data,
        },
    )
