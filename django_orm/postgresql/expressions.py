# -*- coding: utf-8 -*-

from django_orm.core.sql import SqlExpression
from django_orm.utils import remove_diacritic

from .functions import Unaccent

class UnaccentExpression(SqlExpression):
    def __init__(self, field, value):
        super(UnaccentExpression, self)\
            .__init__(Unaccent(self.field), "LIKE", u"%%%s%%" % remove_diacritic(term))
