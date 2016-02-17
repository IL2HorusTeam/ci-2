# -*- coding: utf-8 -*-

import six


def serialize_presets(presets):
    return [
        {
            'title': six.text_type(k.verbose_name),
            'value': v,
        } for k, v in presets.items()
    ]


def serialize_settings(settings):
    result = []

    for tab, parameters in settings.items():
        result.append({
            'tab': {
                'code': tab.name.lower(),
                'title': six.text_type(tab.verbose_name),
            },
            'parameters': [
                {
                    'code': parameter.value,
                    'title': six.text_type(parameter.verbose_name),
                    'help_text': six.text_type(parameter.help_text or '')
                }
                for parameter in parameters
            ],
        })

    return result
