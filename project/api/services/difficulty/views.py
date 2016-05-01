# -*- coding: utf-8 -*-

import itertools

from flask import request

from il2fb.config.difficulty import (
    decompose, autocorrect_difficulty, get_actual_rules, toggle_parameter,
)
from il2fb.config.difficulty.constants import (
    PRESETS, SETTINGS, RULE_TYPES, PARAMETERS,
)
from il2fb.config.difficulty.exceptions import LockedParameterException

from project.api.blueprints import RESTBlueprint
from project.api.response.rest import RESTSuccess, RESTConflict

from .serializers import serialize_presets, serialize_settings


rest = RESTBlueprint(r'difficulty', __name__)


@rest.route(r'/data', methods=['GET'])
def data_view():
    presets = serialize_presets(PRESETS)
    settings = serialize_settings(SETTINGS)
    return RESTSuccess({
        'presets': presets,
        'settings': settings,
    })


@rest.route(r'/decompose', methods=['POST'])
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

    return RESTSuccess({
        'difficulty': difficulty,
        'parameters': parameters,
        'locked': locked,
    })


@rest.route(r'/toggle_parameter', methods=['POST'])
def toggle_parameter_view():
    difficulty = int(request.form['difficulty'])  # without autocorrection

    parameter = request.form['parameter']
    parameter = PARAMETERS.get_by_value(parameter)

    value = request.form['value'] == 'true'

    try:
        difficulty, side_effects = toggle_parameter(difficulty, parameter, value)
    except LockedParameterException as e:
        return RESTConflict(detail=e)

    side_effects = {
        rule_type.name.lower(): [parameter.value for parameter in parameters]
        for rule_type, parameters in side_effects.items()
    }

    return RESTSuccess({
        'difficulty': difficulty,
        'side_effects': side_effects,
    })
