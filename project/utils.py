# -*- coding: utf-8 -*-


# Fake unicode literal support:  Python 3.2 doesn't have the u'' marker for
# literal strings, and alternative solutions like "from __future__ import
# unicode_literals" have other problems (see PEP 414).  u() can be applied
# to ascii strings that include \u escapes (but they must not contain
# literal non-ascii characters).
if not isinstance(b'', type('')):
    def u(s):
        return s
    unicode_type = str
    basestring_type = str
else:
    def u(s):
        return s.decode('unicode_escape')
    # These names don't exist in py3, so use noqa comments to disable
    # warnings in flake8.
    unicode_type = unicode  # noqa
    basestring_type = basestring  # noqa


def import_object(name):
    if isinstance(name, unicode_type) and str is not unicode_type:
        # On python 2 a byte string is required.
        name = name.encode('utf-8')

    if name.count('.') == 0:
        return __import__(name, None, None)

    parts = name.split('.')
    obj = __import__('.'.join(parts[:-1]), None, None, [parts[-1]], 0)

    try:
        return getattr(obj, parts[-1])
    except AttributeError:
        raise ImportError("No module named %s" % parts[-1])
