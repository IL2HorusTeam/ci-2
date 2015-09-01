# -*- coding: utf-8 -*-

import ujson as json


def APIError(error=None, payload=None):
    payload = payload or {}
    payload.update({
        'status': 'error',
        'message': unicode(error or "Request execution error")
    })
    return json.dumps(payload)


def APISuccess(payload=None):
    payload = payload or {}
    payload.update({'status': 'success'})
    return json.dumps(payload)


def APIWarning(payload=None):
    payload = payload or {}
    payload.update({'status': 'warning'})
    return json.dumps(payload)
