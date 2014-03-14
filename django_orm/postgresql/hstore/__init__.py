# -*- coding: utf-8 -*-

from .fields import DictionaryField
from .fields import ReferencesField
from .manager import HStoreManager

from psycopg2.extras import register_hstore

def register_hstore_handler(connection):
    register_hstore(connection.cursor(), globally=True, unicode=True)

from django_orm.dispatch import on_connection_created
on_connection_created.add_single_execution_handler(register_hstore_handler)


__all__ = ['DictionaryField', 'ReferencesField', 'HStoreManager']
