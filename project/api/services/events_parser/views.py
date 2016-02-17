# -*- coding: utf-8 -*-

import traceback
import ujson as json

from geventwebsocket.exceptions import WebSocketError

from il2fb.parsers.events import EventsParser
from il2fb.parsers.events.exceptions import EventParsingError

from project.app import app, sockets
from project.api.response.rest import RESTSuccess
from project.api.response.ws import WSSuccess, WSError, WSWarning

from .helpers import get_supported_events
from .reporting import reporter
from .serializers import shorten_issue


__all__ = ('parse', )

parse_string = EventsParser().parse_string


def get_route(router, path, *args, **kwargs):
    full_path = "/api/v1/events-parser/{0}".format(path)
    return router.route(full_path, *args, **kwargs)


def api_route(path, *args, **kwargs):
    return get_route(app, path, *args, **kwargs)


def ws_route(path, *args, **kwargs):
    return get_route(sockets, path, *args, **kwargs)


@api_route('data', methods=['GET'])
def get_data_view():
    return RESTSuccess({
        'supported_events': get_supported_events(),
    })


class ParseView(object):

    def __call__(self, ws):
        self.ws = ws
        while True:
            data = self.receive_data()
            if data is None:
                break
            else:
                self.try_to_parse_string(data.get('string'))

    def receive_data(self):
        try:
            message = self.ws.receive()
        except WebSocketError:
            message = None

        if message is not None:
            try:
                data = json.loads(message)
            except ValueError as e:
                app.logger.exception(
                    "Failed to read message '{:}':".format(message))
                self.ws.send(WSError(detail=e))
            else:
                return data

    def try_to_parse_string(self, string):
        if string:
            try:
                event = parse_string(string).to_primitive()
            except EventParsingError:
                self.on_error(string)
            else:
                self.ws.send(WSSuccess({'event': event}))
        else:
            self.ws.send(WSError(detail="Nothing to parse."))

    def on_error(self, string):
        app.logger.exception(string)

        similar = map(shorten_issue, reporter.get_similar_issues(title=string))
        payload = {
            'similar': similar,
            'traceback': traceback.format_exc(),
        }

        issue = reporter.get_issue(string)
        if issue:
            issue = shorten_issue(issue)
            payload['issue'] = issue

            if issue['state'] == 'open' or not issue['is_valid']:
                self.ws.send(WSError(payload))
            else:
                self.reopen_issue(issue, payload)
        else:
            self.report_new_issue(string, payload)

    def reopen_issue(self, issue, payload):
        self.ws.send(WSWarning(payload=payload))
        data = self.receive_data()
        if data and data.get('confirm'):
            reporter.reopen_issue(issue)
            self.ws.send(WSSuccess())

    def report_new_issue(self, title, payload):
        self.ws.send(WSWarning(payload=payload))
        data = self.receive_data()
        if data and data.get('confirm'):
            issue = reporter.report_issue(title=title)
            issue = shorten_issue(issue)
            self.ws.send(WSSuccess({'issue': issue}))

parse = ws_route('parse')(ParseView())
