# -*- coding: utf-8 -*-

from django.db import connections, DEFAULT_DB_ALIAS
from django_orm.utils import remove_diacritic

import functools

def _sqlite_unaccent(data):
    if isinstance(data, basestring):
        return remove_diacritic(data)
    return data


SQLITE3_EXTRA_FUNCTIONS = {
    'unaccent': {
        'function':_sqlite_unaccent,
        'params': 1,
    }
}

def ensure_sqlite_function(funcname):
    def _wrapper(function):
        @functools.wraps(function)
        def _fwrapper(self, *args, **kwargs):
            sqlite3_fd = SQLITE3_EXTRA_FUNCTIONS.get(funcname, None)
            if sqlite3_fd:
                sqlite3_fn, sqlite3_params = sqlite3_fd['function'], sqlite3_fd['params']
                dbwrapper = connections[self._db or DEFAULT_DB_ALIAS]
                dbwrapper.connection.create_function("unaccent", sqlite3_params, sqlite3_fn)
            return function(self, *args, **kwargs)
        return _fwrapper
    return _wrapper


__all__ = ['ensure_sqlite_function']
