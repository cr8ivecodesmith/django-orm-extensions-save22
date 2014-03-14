# -*- coding: utf-8 -*-

from psycopg2.extensions import adapt, register_adapter, AsIs, new_type, register_type
from psycopg2.extras import register_composite
import psycopg2

from django.utils.encoding import force_unicode
from django.db import models
from django.db import transaction
from django.db import connection

import re

class ComplexTypeError(Exception):
    pass

# TODO: implement using method

class CompositeField(object):
    """ Composite type base field. """
    _value = None
    _name = None

    def __init__(self, field_repr, coerce=None):
        self.field_repr = field_repr
        self.coerce = coerce

    def __get__(self, instance, owner):
        return self._value or None

    def __set__(self, instance, value):
        self._value = value
        if self.coerce:
            try:
                self._value = self.coerce(self._value)
            except Exception as e:
                raise ComplexTypeError(str(e))

    def _as_sql(self):
        return u"%s %s" % (self._name, self.field_repr)


class CompositeMeta(type):
    def __new__(cls, name, bases, attrs):
        if "order" not in attrs:
            raise Exception("order parameter is mandatory")

        new_class = super(CompositeMeta, cls).__new__(cls, name, bases, attrs)
        new_class._registred = False

        new_class.fields = {}
        for key, value in attrs.iteritems():
            if isinstance(value, CompositeField):
                setattr(value, '_name', key)
                new_class.fields[key] = value
        
        if new_class.fields:
            new_class.assign_dinamic_methods()
        return new_class

    def __init__(cls, name, bases, attrs):
        super(CompositeMeta, cls).__init__(name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        instance = super(CompositeMeta, cls).__call__(*args, **kwargs)
        if not cls._registred:
            with transaction.commit_manually():
                try:
                    cls.register_type_globaly()
                    transaction.commit()
                except psycopg2.ProgrammingError:
                    transaction.rollback()

                    cursor = connection.cursor()
                    cursor.execute(cls._create_sql_raw)
                    cls.register_type_globaly()
                    transaction.commit()

            cls._registred = True
        return instance

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

    def type_name(cls):
        return cls.__name__.lower()

    def assign_dinamic_methods(cls):
        sql_fields_raw = u",\n    ".join([x._as_sql() for x in \
            [cls.fields[oi] for oi in cls.order]])

        template = u"CREATE TYPE %s AS (\n    %s\n);"
        create_sql_raw = template % (cls.type_name(), sql_fields_raw)

        # Assign staticaly generated raw sql unicode string
        cls.add_to_class('_create_sql_raw', create_sql_raw)
        cls.add_to_class('_create_sql', lambda self: self._create_sql_raw)
        cls.add_to_class('_as_sql_template', u"ROW(%s)")
        
        def _wrapper(self):
            items = []
            for item in [self.fields[oi]._value for oi in self.order]:
                if isinstance(item, (long, int, float)):
                    items.append(unicode(item))
                elif isinstance(item, CompositeType):
                    items.append(item._as_sql())
                else:
                    items.append("'%s'" % (unicode(item)))

            return self._as_sql_template % (u", ".join(items))

        cls.add_to_class('_as_sql', _wrapper)

    @transaction.commit_on_success
    def register_type_globaly(cls):
        cursor = connection.cursor()
        register_composite(cls.type_name(), cursor, globally=True)
        register_adapter(cls, lambda obj: AsIs(obj._as_sql()))
        print "Registering %s type" % (cls.type_name())


class CompositeType(object):
    """ Composite tybe base class. """

    __metaclass__ = CompositeMeta
    order = ()

    def __init__(self, *args, **kwargs):
        if len(args) > 0 and len(args) == len(order):
            try:
                for oitem in self.order:
                    setattr(self, oitem, args.pop())
            except IndexError:
                pass
        elif kwargs:
            for oitem in self.order:
                setattr(self, oitem, kwargs.get(oitem, None))

    def _with_wrapper(self, wrapper):
        for oitem in self.order:
            setattr(self, oitem, getattr(wrapper, oitem, None))

    def __repr__(self):
        return u"<CompositeType %s>" % (
            ", ".join(["%s=%s" % (x._name, x._value) \
                for x in self.fields.itervalues()]))

    def quote_name(self, name):
        if name.startswith('"') and name.endswith('"'):
            return name # Quoting once is enough.
        return '"%s"' % name


class CompositeModelField(models.Field):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self._type = kwargs.pop('type')
        super(CompositeModelField, self).__init__(*args, **kwargs)

    def get_prep_lookup(self, lookup_type, value):
        return value

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        return self.get_prep_lookup(lookup_type, value)

    def db_type(self, connection):
        return self._type.__class__.type_name()

    def to_python(self, value):
        if value and isinstance(value, (list,tuple)):
            obj = self._type.__class__()
            obj._with_wrapper(value)
            return obj
        return value


class C(object):
    """
    Posible query string:
        "(boss).person.name == ?"
        "(boss).cualify  >= ?"
        "(boss).account.name LIKE %?%"
    """

    def __init__(self, querystring, *args, **kwargs):
        self.qstr = querystring
        self.qstrl = querystring.lower()
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        # unaccent(%s) LIKE unaccent(%%s)
        # ('lower(unaccent(%s)) LIKE lower(unaccent(%%s))'
        qstr = self.qstr

        if "iunaccent" in self.qstrl:
            p1, p2, p3 = self.qstr.split(maxsplit=3)
            qstr = u" ".join([u"lower(unaccent(%s))" % p1, u'LIKE', u"lower(unaccent(%s))" % p3])

        elif "unaccent" in self.qstrl:
            p1, p2, p3 = re.split(r'\s', self.qstr, 3, re.U)
            qstr = u" ".join([u"unaccent(%s)" % p1, u'LIKE', "unaccent(%s)" % p3])

        qstr = qstr.replace("?", "%s") \
            if "like" not in self.qstr.lower() \
            else self.qstr.replace("?", "%s")

        return (qstr, list(self.args))
