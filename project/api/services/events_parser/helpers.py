# coding: utf-8

import six

from operator import itemgetter


def get_supported_events():
    from il2fb.parsers.events.events import get_all_events

    def description(structure):
        return six.text_type(
            structure.__doc__.strip().replace('::', ':').replace('    ', '')
        )

    result = (
        (six.text_type(x.verbose_name), description(x))
        for x in get_all_events()
    )
    return sorted(result, key=itemgetter(0))
