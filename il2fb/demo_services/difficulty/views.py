# coding: utf-8

import itertools

from il2fb.config.difficulty import decompose, autocorrect_difficulty
from il2fb.config.difficulty import get_actual_rules, toggle_parameter
from il2fb.config.difficulty.constants import PRESETS, SETTINGS, RULE_TYPES
from il2fb.config.difficulty.constants import PARAMETERS
from il2fb.config.difficulty.exceptions import LockedParameterException

from il2fb.demo_services.core import json
from il2fb.demo_services.core.response.rest import RESTSuccess, RESTConflict

from .serializers import serialize_presets, serialize_settings


async def http_get_data(request):
    pretty = 'pretty' in request.query
    presets = serialize_presets(PRESETS)
    settings = serialize_settings(SETTINGS)
    return RESTSuccess(
        payload={
            'presets': presets,
            'settings': settings,
        },
        pretty=pretty,
    )


async def http_decompose_difficulty(request):
    pretty = 'pretty' in request.query
    body = await request.json(loads=json.loads)
    difficulty = int(body['difficulty'])
    difficulty, _ = autocorrect_difficulty(difficulty)

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

    return RESTSuccess(
        payload={
            'difficulty': difficulty,
            'parameters': parameters,
            'locked': locked,
        },
        pretty=pretty,
    )


async def http_toggle_parameter(request):
    pretty = 'pretty' in request.query
    body = await request.json(loads=json.loads)

    difficulty = int(body['difficulty'])  # without autocorrection

    parameter = body['parameter']
    parameter = PARAMETERS.get_by_value(parameter)

    value = body['value']

    try:
        difficulty, side_effects = toggle_parameter(
            difficulty, parameter, value,
        )
    except LockedParameterException as e:
        return RESTConflict(detail=e)

    side_effects = {
        rule_type.name.lower(): [parameter.value for parameter in parameters]
        for rule_type, parameters in side_effects.items()
    }

    return RESTSuccess(
        payload={
            'difficulty': difficulty,
            'side_effects': side_effects,
        },
        pretty=pretty,
    )
