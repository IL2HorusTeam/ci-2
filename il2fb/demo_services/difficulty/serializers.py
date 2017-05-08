# coding: utf-8


def serialize_presets(presets):
    return [
        {
            'title': str(k.verbose_name),
            'value': v,
        } for k, v in presets.items()
    ]


def serialize_settings(settings):
    result = []

    for tab, parameters in settings.items():
        result.append({
            'tab': {
                'code': tab.name.lower(),
                'title': str(tab.verbose_name),
            },
            'parameters': [
                {
                    'code': parameter.value,
                    'title': str(parameter.verbose_name),
                    'help_text': str(parameter.help_text or '')
                }
                for parameter in parameters
            ],
        })

    return result
