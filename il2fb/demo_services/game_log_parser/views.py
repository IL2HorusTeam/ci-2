# coding: utf-8

import logging
import traceback

from aiohttp import web, WSMsgType
from il2fb.commons.events import EventParsingException

from il2fb.demo_services.core import json
from il2fb.demo_services.core.response.rest import RESTSuccess
from il2fb.demo_services.core.response.ws import WSSuccess, WSError, WSWarning

from .helpers import get_supported_events


LOG = logging.getLogger(__name__)


async def http_health(request):
    pretty = 'pretty' in request.query
    return RESTSuccess(payload={'status': 'alive'}, pretty=pretty)


async def http_get_data(request):
    pretty = 'pretty' in request.query
    return RESTSuccess(
        payload={
            'supported_events': get_supported_events(),
        },
        pretty=pretty,
    )


class WSParseView(web.View):
    _ws = None

    async def get(self):
        LOG.debug("ws connection created")

        self._ws = web.WebSocketResponse()
        await self._ws.prepare(self.request)

        async for msg in self._ws:
            if msg.type == WSMsgType.TEXT:
                await self.on_message(msg.data)
            elif msg.type == WSMsgType.ERROR:
                LOG.error(
                    "ws connection closed with exception: {}"
                    .format(self._ws.exception())
                )

        LOG.debug("ws connection closed")
        return self._ws

    async def on_message(self, message):
        if message == 'close':
            await self._ws.close()
        else:
            data = json.loads(message)
            await self.on_data(data)

    async def on_data(self, data):
        string = data.get('string')
        if string:
            try:
                event = self.request.app['game_log_parser'].parse(string)
            except EventParsingException:
                LOG.exception("Failed to parse string `{}`".format(string))
                await self.on_parsing_error(string)
            else:
                self._ws.send_str(WSSuccess({'event': event.to_primitive()}))
        else:
            self._ws.send_str(WSError(detail="Got no data to parse."))

    async def on_parsing_error(self, string):
        reporter = self.request.app['bug_reporter']

        similar_issues = await reporter.get_similar_issues(title=string)
        similar_issues = list(map(reporter.shorten_issue, similar_issues))
        payload = {
            'similar': similar_issues,
            'traceback': traceback.format_exc(),
        }

        issue = await reporter.get_issue(string)
        if issue:
            issue = reporter.shorten_issue(issue)
            payload['issue'] = issue

            if issue['state'] == 'open' or not issue['is_valid']:
                self._ws.send_str(WSError(payload))
            else:
                await self.reopen_issue(issue, payload)
        else:
            await self.report_new_issue(string, payload)

    async def reopen_issue(self, issue, payload):
        reporter = self.request.app['bug_reporter']
        self._ws.send_str(WSWarning(payload=payload))

        message = await self._ws.receive_str()
        message = json.loads(message)
        if message and message.get('confirm'):
            await reporter.reopen_issue(issue)
            self._ws.send_str(WSSuccess())

    async def report_new_issue(self, title, payload):
        reporter = self.request.app['bug_reporter']
        self._ws.send_str(WSWarning(payload=payload))

        message = await self._ws.receive_str()
        message = json.loads(message)
        if message and message.get('confirm'):
            issue = await reporter.report_issue(title=title)
            issue = reporter.shorten_issue(issue)
            self._ws.send_str(WSSuccess({'issue': issue}))
