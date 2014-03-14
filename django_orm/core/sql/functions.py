# -*- coding: utf-8 -*-

from .base import SqlNode
from .utils import _setup_joins_for_fields

# TODO: add function(function()) feature.

class SqlFunction(SqlNode):
    sql_template = '%(function)s(%(field)s)'
    sql_function = None
    args = []

    def __init__(self, field, *args, **kwargs):
        self.field = field
        self.args = args
        self.extern_params = kwargs

    @property
    def field_parts(self):
        return self.field.split("__")
    
    def as_sql(self, qn, queryset):
        """
        Return the aggregate/annotation rendered as sql.
        """

        _setup_joins_for_fields(self.field_parts, self, queryset)

        params = {}
        if self.sql_function is not None:
            params['function'] = self.sql_function
        if isinstance(self.field, basestring):
            params['field'] = qn(self.field)
        elif isinstance(self.field, (tuple, list)):
            _tbl, _fld = self.field
            params['field'] = "%s.%s" % (qn(_tbl), qn(_fld))
        else:
            raise ValueError("Invalid field value")

        params.update(self.extern_params)
        return self.sql_template % params, self.args
