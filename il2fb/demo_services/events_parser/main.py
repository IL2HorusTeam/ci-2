#!/usr/bin/env python3
# coding: utf-8

import argparse
import asyncio
import logging
import logging.config
import pathlib

from aiohttp import web

import aiohttp_cors

from il2fb.parsers.events import EventsParser

from .config import load_config
from .reporter import setup_reporter
from .routes import setup_routes


__here__ = pathlib.Path(__file__).absolute().parent


def load_args():
    parser = argparse.ArgumentParser(
        description="Demo service of 'il2fb-events-parser' library"
    )
    parser.add_argument(
        '-c', '--config',
        dest='config_path',
        type=str,
        default=None,
        help="path to config. Default values will be used if not specified",
    )
    return parser.parse_args()


def build_app(loop, config, **kwargs):
    app = web.Application(loop=loop, **kwargs)
    app['config'] = config
    app['events_parser'] = EventsParser()

    setup_routes(app)
    setup_cors(app)
    setup_reporter(app, loop)

    return app


def setup_cors(app):
    defaults = {
        key: aiohttp_cors.ResourceOptions(**value)
        for key, value in app['config']['cors'].items()
    }
    cors = aiohttp_cors.setup(app, defaults=defaults)

    for route in app.router.routes():
        cors.add(route)


def main():
    loop = asyncio.get_event_loop()

    args = load_args()
    config = load_config(args.config_path)

    logging.config.dictConfig(config['logging'])
    app = build_app(
        loop,
        debug=config.pop('debug', False),
        config=config,
    )
    web.run_app(
        app,
        host=config['bind']['address'],
        port=config['bind']['port'],
        access_log_format=config['access_log_format'],
    )


if __name__ == '__main__':
    main()
