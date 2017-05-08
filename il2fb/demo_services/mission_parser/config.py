# coding: utf-8

import copy

import yaml

from jsonschema import validate

from il2fb.demo_services.core.utils import update_nested_dict


CONFIG_SCHEMA = {
    'type': 'object',
    'properties': {
        'bind': {
            'type': 'object',
            'properties': {
                'address': {
                    'format': 'hostname',
                },
                'port': {
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 65535,
                },
            },
            'required': ['address', 'port', ]
        },
        'debug': {
            'type': 'boolean',
        },
        'logging': {
            'type': 'object',
        },
        'access_log_format': {
            'type': 'string',
        },
        'cors': {
            'type': 'object',
        },
        'mission_max_size': {
            'type': 'integer',
            'minimum': 0,
        },
        'github': {
            'type': 'object',
            'properties': {
                'access_token': {
                    'type': 'string',
                },
                'repo_owner': {
                    'type': 'string',
                },
                'repo_name': {
                    'type': 'string',
                },
            },
            'required': ['access_token', 'repo_owner', 'repo_name', ],
        },
    },
    'required': [
        'bind', 'logging', 'access_log_format', 'github', 'mission_max_size',
    ]
}

CONFIG_DEFAULTS = {
    'bind': {
        'address': "127.0.0.1",
        'port': 5000,
    },
    'debug': False,
    'logging': {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '[%(levelname)-8s %(asctime)s %(name)s] %(message)s',
                'datefmt': '%Y-%m-%dT%H:%M:%S%z',
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    },
    'access_log_format': (
        '%a %l %u "%r" %s %b %Dms "%{Referrer}i" "%{User-Agent}i"'
    ),
    'cors': {},
    'mission_max_size': 1 * 1024 * 1024,  # 1 MiB for uploads
}


def load_config(path=None):
    config = copy.deepcopy(CONFIG_DEFAULTS)

    if path:
        with open(path, 'r') as f:
            custom = yaml.load(f.read())
            if custom:
                update_nested_dict(config, custom)

    validate(config, CONFIG_SCHEMA)
    return config
