# coding: utf-8

import traceback

from il2fb.parsers.events import EventsParser
from il2fb.parsers.events.exceptions import EventParsingError

from project.app import app
from project.api.blueprints import RESTBlueprint, WSBlueprint
from project.api.views import WebSocketView
from project.api.response.rest import RESTSuccess
from project.api.response.ws import WSSuccess, WSError, WSWarning

from .helpers import get_supported_events
from .reporting import reporter


rest = RESTBlueprint(r'events-parser', __name__)
ws = WSBlueprint(r'events-parser', __name__)

parse_string = EventsParser().parse_string


@rest.route(r'/data', methods=['GET'])
def get_data():
    return RESTSuccess({
        'supported_events': get_supported_events(),
    })


class ParseView(WebSocketView):

    def on_message(self, message):
        string = message.get('string')
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

        similar = map(reporter.shorten_issue,
                      reporter.get_similar_issues(title=string))
        payload = {
            'similar': similar,
            'traceback': traceback.format_exc(),
        }

        issue = reporter.get_issue(string)
        if issue:
            issue = reporter.shorten_issue(issue)
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
            issue = reporter.shorten_issue(issue)
            self.ws.send(WSSuccess({'issue': issue}))


ws.add_view_url_rule(r'/parse', ParseView)
