# coding: utf-8

import ujson as json
import six


def WSSuccess(payload=None, detail=None):
    payload = payload or {}
    payload['status'] = 'success'
    if detail:
        payload['detail'] = six.text_type(detail)
    return json.dumps(payload)


def WSWarning(payload=None, detail=None):
    payload = payload or {}
    payload['status'] = 'warning'
    if detail:
        payload['detail'] = six.text_type(detail)
    return json.dumps(payload)


def WSError(payload=None, detail=None):
    payload = payload or {}
    payload.update({
        'status': 'error',
        'detail': six.text_type(detail or "Request execution error."),
    })
    return json.dumps(payload)
