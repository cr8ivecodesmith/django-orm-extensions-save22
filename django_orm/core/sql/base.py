# -*- coding: utf-8 -*-

class SqlNode(object):
    negated = False

    sql_negated_template = "NOT %s"

    @property
    def field_parts(self):
        raise NotImplementedError

    def as_sql(self, qn, queryset):
        raise NotImplementedError

    def __invert__(self):
        # TODO: use clone insetead self modification.
        self.negated = True
        return self

