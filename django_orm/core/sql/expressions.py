# -*- coding: utf-8 -*-

from django.utils import tree
from django.db.models.sql.datastructures import MultiJoin

from .base import SqlNode
from .utils import _setup_joins_for_fields

# TODO: can negate sql expression.

class SqlExpression(SqlNode):
    sql_template = "%(field)s %(operator)s %%s"

    def __init__(self, field_or_func, operator, value=None, **kwargs):
        self.operator = operator
        self.value = value
        self.extra = kwargs

        if isinstance(field_or_func, SqlNode):
            self.field = field_or_func.field
            self.sql_function = field_or_func
        else:
            self.field = field_or_func
            self.sql_function = None

    @property
    def field_parts(self):
        return self.field.split("__")

    def as_sql(self, qn, queryset):
        """
        Return the statement rendered as sql.
        """

        # setup joins if needed
        if self.sql_function is None:
            _setup_joins_for_fields(self.field_parts, self, queryset)
        
        # build sql
        params, args = {}, []

        if self.operator is not None:
            params['operator'] = self.operator
            
        if self.sql_function is None:
            if isinstance(self.field, basestring):
                params['field'] = qn(self.field)
            elif isinstance(self.field, (tuple, list)):
                _tbl, _fld = self.field
                params['field'] = "%s.%s" % (qn(_tbl), qn(_fld))
            else:
                raise ValueError("Invalid field value")
        else:
            params['field'], _args = self.sql_function.as_sql(qn, queryset)
            args.extend(_args)

        params.update(self.extra)
        if self.value is not None:
            args.extend([self.value])

        template_result = self.sql_template % params

        if self.negated:
            return self.sql_negated_template % (template_result), args

        return template_result, args


class RawExpression(SqlExpression):
    field_parts = []

    def __init__(self, sqlstatement, *args):
        self.statement = sqlstatement
        self.params = args

    def as_sql(self, qn, queryset):
        return self.statement, self.params

