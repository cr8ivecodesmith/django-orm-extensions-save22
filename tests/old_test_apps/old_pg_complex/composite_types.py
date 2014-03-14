# -*- coding: utf-8 -*-

from django_orm.postgresql.composite import CompositeType, CompositeField

class Person(CompositeType):
    name = CompositeField('varchar(255)')
    age = CompositeField('integer')

    order = ('name', 'age')


class Account(CompositeType):
    person = CompositeField('person')
    date = CompositeField('timestamp')

    order = ('person', 'date')


__register__ = ['Person', 'Account']
