# -*- coding: utf-8 -*-

from .reporting import reporter


def shorten_issue(x):
    return {
        'number': x['number'],
        'url': x['html_url'],
        'state': x['state'],
        'is_valid': reporter.is_valid(x),
    }
