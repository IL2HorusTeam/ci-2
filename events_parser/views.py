import logging
import traceback

from il2fb.commons.events import EventParsingException
from il2fb.parsers.game_log import GameLogEventParser

from demo_services.core import json
from demo_services.core.cors import with_cors
from demo_services.core.response import RESTSuccess, RESTBadRequest
from demo_services.core.response import RESTUnsupportedMediaType

from demo_services.events_parser.helpers import get_supported_events


LOG = logging.getLogger(__name__)
PARSER = GameLogEventParser()
SUPPORTED_EVENTS = get_supported_events()


@with_cors(
    allow_methods=('GET', 'OPTIONS'),
)
def get_data(request):
    pretty = 'pretty' in request.args
    payload = {
        'supported_events': SUPPORTED_EVENTS,
    }
    return RESTSuccess(payload, pretty=pretty)


@with_cors(
    allow_methods=('POST', 'OPTIONS'),
    allow_headers='Content-Type',
)
def parse(request):
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

    if not content:
        return RESTBadRequest(
            detail="No pata to parse",
            pretty=pretty,
        )

    results = []

    for line in content:
        try:
            event = PARSER.parse(line)
        except EventParsingException:
            item = dict(
                status='error',
                line=line,
                traceback=traceback.format_exc(),
            )
        else:
            item = dict(
                status='ok',
                line=line,
                event=event.to_primitive(),
            )
        finally:
            results.append(item)

    return RESTSuccess(
        payload={
            'data': results,
        },
        pretty=pretty,
    )
