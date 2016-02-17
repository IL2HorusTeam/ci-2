# -*- coding: utf-8 -*-

import six

from operator import itemgetter


def get_supported_events():
    import il2fb.parsers.events.structures.events as events_structures

    def description(structure):
        return six.text_type(
            structure.__doc__.strip().replace('::', ':').replace('    ', '')
        )

    result = (
        getattr(events_structures, name)
        for name in events_structures.__all__
    )
    result = (
        (six.text_type(x.verbose_name), description(x))
        for x in result
    )
    return sorted(result, key=itemgetter(0))
