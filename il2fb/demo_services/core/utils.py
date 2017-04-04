# coding: utf-8

import collections


def update_nested_dict(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update_nested_dict(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]

    return d
