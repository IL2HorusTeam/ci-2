# -*- coding: utf-8 -*-

import itertools
import six

from flask import jsonify, request

from il2fb.config.difficulty import (
    decompose, autocorrect_difficulty, get_actual_rules, toggle_parameter,
)
from il2fb.config.difficulty.constants import (
    PRESETS, SETTINGS, RULE_TYPES, PARAMETERS,
)
from il2fb.config.difficulty.exceptions import LockedParameterException

from ..app import app


__all__ = ('data_view', 'decompose_view', 'toggle_parameter_view', )


def route(path, *args, **kwargs):
    return app.route("/api/v1/difficulty/{0}".format(path), *args, **kwargs)


@route('data', methods=['GET'])
def data_view():
    presets = serialize_presets(PRESETS)
    settings = serialize_settings(SETTINGS)

    return jsonify(presets=presets, settings=settings)


@route('decompose', methods=['POST'])
def decompose_view():
    difficulty = int(request.form['difficulty'])
    difficulty, __ = autocorrect_difficulty(difficulty)

    parameters = {
        parameter.value: value
        for parameter, value in decompose(difficulty).items()
    }

    actual_rules = get_actual_rules(difficulty).values()
    locked = [
        rules[RULE_TYPES.LOCKS]
        for rules in actual_rules
        if RULE_TYPES.LOCKS in rules
    ]
    locked = [
        parameter.value
        for parameter in set(itertools.chain(*locked))
    ]

    return jsonify(difficulty=difficulty, parameters=parameters, locked=locked)


@route('toggle_parameter', methods=['POST'])
def toggle_parameter_view():
    difficulty = int(request.form['difficulty'])  # without autocorrection

    parameter = request.form['parameter']
    parameter = PARAMETERS.get_by_value(parameter)

    value = request.form['value'] == 'true'

    try:
        difficulty, side_effects = toggle_parameter(difficulty,
                                                    parameter,
                                                    value)
    except LockedParameterException as e:
        return jsonify(error=six.text_type(e))

    side_effects = {
        rule_type.name.lower(): [parameter.value for parameter in parameters]
        for rule_type, parameters in side_effects.items()
    }

    return jsonify(difficulty=difficulty, side_effects=side_effects)


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
