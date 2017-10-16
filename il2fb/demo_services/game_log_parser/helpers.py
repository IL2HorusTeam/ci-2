# coding: utf-8

from operator import itemgetter

from il2fb.parsers.game_log.events import get_all_events


def get_supported_events():

    def description(structure):
        return str(
            structure.__doc__.strip().replace('::', ':').replace('    ', '')
        )

    result = (
        (str(x.verbose_name), description(x))
        for x in get_all_events()
    )
    return sorted(result, key=itemgetter(0))
