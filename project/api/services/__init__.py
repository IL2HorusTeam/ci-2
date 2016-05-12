# coding: utf-8

from project.utils import import_object


def register_blueprints(target, blueprints):
    for url_prefix, blueprint_path in blueprints:
        blueprint = import_object("{}.{}".format(__package__, blueprint_path))
        target.register_blueprint(blueprint, url_prefix=url_prefix)


def register_rest_blueprints(app):
    register_blueprints(app, [
        (r'/api/difficulty', 'difficulty.views.rest'),
        (r'/api/mission-parser', 'mission_parser.views.rest'),
        (r'/api/events-parser', 'events_parser.views.rest'),
    ])


def register_ws_blueprints(sockets):
    register_blueprints(sockets, [
        (r'/api/events-parser', 'events_parser.views.ws'),
    ])
