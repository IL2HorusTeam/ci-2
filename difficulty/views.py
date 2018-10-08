from itertools import chain

from il2fb.config.difficulty import decompose, autocorrect_difficulty
from il2fb.config.difficulty import get_actual_rules, toggle_parameter
from il2fb.config.difficulty.constants import PRESETS, SETTINGS, RULE_TYPES
from il2fb.config.difficulty.constants import PARAMETERS
from il2fb.config.difficulty.exceptions import LockedParameterException

from demo_services.core.response import RESTSuccess, RESTConflict
from demo_services.core.cors import with_cors

from demo_services.difficulty.serializers import serialize_presets
from demo_services.difficulty.serializers import serialize_settings


@with_cors(
    allow_methods=('GET', 'OPTIONS'),
)
def get_data(request):
    pretty = 'pretty' in request.args
    presets = serialize_presets(PRESETS)
    settings = serialize_settings(SETTINGS)
    payload = {
        'presets': presets,
        'settings': settings,
    }
    return RESTSuccess(payload, pretty=pretty)


@with_cors(
    allow_methods=('POST', 'OPTIONS'),
    allow_headers='Content-Type',
)
def decompose_value(request):
    pretty = 'pretty' in request.args
    body = request.get_json()

    difficulty = int(body['difficulty'])
    difficulty, _ = autocorrect_difficulty(difficulty)

    actual_rules = get_actual_rules(difficulty).values()
    locked = [
        rules[RULE_TYPES.LOCKS]
        for rules in actual_rules
        if RULE_TYPES.LOCKS in rules
    ]
    locked = [
        parameter.value
        for parameter in set(chain(*locked))
    ]

    parameters = {
        parameter.value: value
        for parameter, value in decompose(difficulty).items()
    }

    payload = {
        'difficulty': difficulty,
        'locked': locked,
        'parameters': parameters,
    }

    return RESTSuccess(payload, pretty=pretty)


@with_cors(
    allow_methods=('POST', 'OPTIONS'),
    allow_headers='Content-Type',
)
def toggle_value(request):
    pretty = 'pretty' in request.args
    body = request.get_json()

    difficulty = int(body['difficulty'])

    parameter = body['parameter']
    parameter = PARAMETERS.get_by_value(parameter)

    value = body['value']

    try:
        difficulty, side_effects = toggle_parameter(
            difficulty, parameter, value,
        )
    except LockedParameterException:
        return RESTConflict()

    side_effects = {
        rule_type.name.lower(): [parameter.value for parameter in parameters]
        for rule_type, parameters in side_effects.items()
    }
    payload = {
        'difficulty': difficulty,
        'side_effects': side_effects,
    }

    return RESTSuccess(payload, pretty=pretty)
