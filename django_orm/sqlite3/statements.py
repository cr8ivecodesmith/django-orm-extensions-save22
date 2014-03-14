# -*- coding: utf-8 -*-

# NOTE: this module is pending to refactor.

from django_orm.utils.statements import BaseTree as CommonBaseTree
from django_orm.sqlite3.extra_functions import ensure_sqlite_function


class BaseTree(CommonBaseTree):
    pass


class Unaccent(BaseTree):
    def sql_condition(self, parts, value, qn):
        key = self.key_to_quoted_field_name(parts, qn)
        if not self.negated:
            sql = "unaccent(%s) LIKE unaccent(%%s) ESCAPE '\\'" % (key)
        else:
            sql = "unaccent(%s) NOT LIKE unaccent(%%s) ESCAPE '\\'" % (key)

        return sql, [self._prepare_search_term(value)]

    def _prepare_search_term(self, term):
        return u"%%%s%%" % term
