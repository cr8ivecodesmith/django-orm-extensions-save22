# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import force_unicode


class ArrayField(models.Field):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self._array_type = kwargs.pop('dbtype', 'int')
        kwargs.setdefault('blank', True)
        kwargs.setdefault('null', True)
        kwargs.setdefault('default', None)
        super(ArrayField, self).__init__(*args, **kwargs)

    def get_prep_lookup(self, lookup_type, value):
        """
        Perform preliminary non-db specific lookup checks and conversions
        """

        if hasattr(value, 'prepare'):
            return value.prepare()
        if hasattr(value, '_prepare'):
            return value._prepare()

        return self.get_prep_value(value)

    def db_type(self, connection):
        return '%s[]' % self._array_type

    def get_db_prep_value(self, value, connection, prepared=False):
        value = value if prepared else self.get_prep_value(value)
        if not value or isinstance(value, basestring):
            return value

        if self._array_type in ('text') or "varchar" in self._array_type:
            value = map(force_unicode, value)

        return value

    def get_prep_value(self, value):
        return value

    def to_python(self, value):
        if value and isinstance(value, (list,tuple)):
            if self._array_type in ('text') or "varchar" in self._array_type:
                return map(force_unicode, value)
        return value

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([
        (
            [ArrayField], # class
            [],               # positional params
            {'dbtype': ["_array_type", {"default" : "int"}]}, # kwargs
        )
    ], ['django_orm\.postgresql\.fields\.arrays\.ArrayField'])
except ImportError:
    pass
