# coding: utf-8

from project.utils.lang import import_object


def health():
    return ('', 200)


def register_blueprints(target, blueprints):
    for url_prefix, blueprint_path in blueprints:
        blueprint = import_object("{}.{}".format(__package__, blueprint_path))
        target.register_blueprint(blueprint, url_prefix=url_prefix)


def register_rest_blueprints(app):
    register_blueprints(app, [
        (r'/difficulty', 'difficulty.views.rest'),
        (r'/mission-parser', 'mission_parser.views.rest'),
        (r'/events-parser', 'events_parser.views.rest'),
        (r'/ds-config', 'ds_config.views.rest'),
    ])
    app.route(r'/health')(health)


def register_ws_blueprints(sockets):
    register_blueprints(sockets, [
        (r'/events-parser', 'events_parser.views.ws'),
    ])
