# -*- coding: utf-8 -*-

from django.utils.datastructures import SortedDict
from django.db.models.sql.where import ExtraWhere

from .sql.tree import AND, OR
from .sql.utils import _setup_joins_for_fields


class StatementMixIn(object):
    def annotate_functions(self, **kwargs):
        extra_select, params = SortedDict(), []
        clone = self._clone()

        for alias, node in kwargs.iteritems():
            _sql, _params = node.as_sql(self.quote_name, self)

            extra_select[alias] = _sql
            params.extend(_params)

        clone.query.add_extra(extra_select, params, None, None, None, None)
        return clone

    def where(self, *args):
        clone = self._clone()
        statement = AND(*args)

        _sql, _params = statement.as_sql(self.quote_name, clone)
        if hasattr(_sql, 'to_str'):
            _sql = _sql.to_str()

        clone.query.where.add(ExtraWhere([_sql], _params), "AND")
        return clone
