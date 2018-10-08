#!/usr/bin/env python3

import importlib
import os
import sys

from pathlib import Path

import yaml

from flask import Flask
from flask.views import View

from demo_services.core.cors import CORS_ALLOW_ORIGIN_ENV_VAR_NAME
from demo_services.core.utils import with_request


__here__ = Path(__file__).parent.absolute()

ENDPOINTS_PATH = __here__ / 'local_endpoints.yml'
FUNCTIONS_PATH = __here__ / 'functions.yml'


def load_object(reference):
    module_name, function_name = reference.split(':', 1)
    module = (
           sys.modules.get(module_name)
        or importlib.import_module(module_name)
    )
    handler = getattr(module, function_name)

    if isinstance(handler, View):
        handler = handler.as_view(name=reference)

    return handler


def load_endpoints():
    with open(FUNCTIONS_PATH) as f:
        functions = yaml.load(f)
        functions = {
            item['name']: load_object(item['handler'])
            for item in functions
        }

    with open(ENDPOINTS_PATH) as f:
        endpoints = yaml.load(f)

    return [
        (
            "/{}".format(endpoint['name']),
            endpoint['name'],
            functions[endpoint['name']],
            endpoint['methods'],
        )
        for endpoint in endpoints
    ]


def main():
    os.environ[CORS_ALLOW_ORIGIN_ENV_VAR_NAME] = '*'
    app = Flask(__name__)
    endpoints = load_endpoints()

    for rule, name, handler, methods in endpoints:
        app.add_url_rule(
            rule=rule,
            endpoint=name,
            view_func=with_request(handler),
            methods=methods,
        )

    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
    )


if __name__ == '__main__':
    main()
