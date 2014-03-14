# -*- coding: utf-8 -*-
from django.db.models import signals
from django.db.backends import signals as backend_signals
from django.db.utils import DatabaseError
from django.conf import settings
from django.utils.importlib import import_module

import logging; log = logging.getLogger('orm.cache')

DEFAULT_CACHE_TIMEOUT = getattr(settings, 'ORM_CACHE_DEFAULT_TIMEOUT', 60)
DEFAULT_CACHE_ENABLED = getattr(settings, 'ORM_CACHE_DEFAULT_ENABLED', False)

class OrmMeta(object):
    options = {
        'cache_object': DEFAULT_CACHE_ENABLED,
        'cache_queryset': DEFAULT_CACHE_ENABLED,
        'default_timeout': DEFAULT_CACHE_TIMEOUT,
    }


def ensure_default_manager(sender, **kwargs):
    from django_orm.cache.utils import get_cache_key_for_pk
    from django_orm.cache.invalidator import invalidate_object
    from django.db import models

    meta_orm_class = getattr(sender, 'OrmMeta', None)
    if not meta_orm_class:
        meta_orm_obj = OrmMeta()
    else:
        meta_orm_obj = meta_orm_class()
        options = getattr(meta_orm_obj, 'options', {})

        if 'cache_object' not in options:
            options['cache_object'] = DEFAULT_CACHE_ENABLED
        
        if 'default_timeout' not in options:
            options['default_timeout'] = DEFAULT_CACHE_TIMEOUT

        meta_orm_obj.options = options
    
    sender.add_to_class('_orm_meta', meta_orm_obj)
    sender.add_to_class('_get_cache_key_for_pk', 
        staticmethod(lambda x,y: get_cache_key_for_pk(x, y)))
    sender.add_to_class('cache_key', 
        property(lambda x: x._get_cache_key_for_pk(x.__class__, x.pk)))


signals.class_prepared.connect(ensure_default_manager)

class ConnectionCreateHandler(object):
    default_function = lambda x,y: None
    single_execution_handlers = {}
    execution_handlers = {}

    def __call__(self, sender, connection, **kwargs):
        internal_handler = getattr(self, 'on_%s_connection_created' % (connection.vendor))
        internal_handler(connection)

        if self.single_execution_handlers:
            valid_handlers = filter(lambda v: v._vendor in ['all', connection.vendor],
                self.single_execution_handlers.itervalues())

            for valid_handler in valid_handlers:
                del self.single_execution_handlers[valid_handler.__name__]
                valid_handler(connection)
        
    def on_postgresql_connection_created(self, connection):
        #print "Postgresql:", connection
        pass

    def on_mysql_connection_created(self, connection):
        #print "MySQL:", connection
        pass

    def on_sqlite_connection_created(self, connection):
        #print "Sqlite3:", connection
        pass

    def add_single_execution_handler(self, function, vendor='all'):
        function._vendor = vendor
        self.single_execution_handlers[function.__name__] = function


on_connection_created = ConnectionCreateHandler()
backend_signals.connection_created.connect(on_connection_created)
