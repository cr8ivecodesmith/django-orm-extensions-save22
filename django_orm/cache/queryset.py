# -*- coding: utf-8 -*-

from django.db.models.query import QuerySet
from django.db.models.query import ITER_CHUNK_SIZE
from django.db import backend, connection
from django.conf import settings

from django_orm.cache.exceptions import CacheMissingWarning
from .utils import get_cache_key_for_pk, get_cache

import copy
import hashlib
import logging


CACHE_KEY_PREFIX = getattr(settings, 'ORM_CACHE_KEY_PREFIX', 'orm.cache')
CACHE_FETCH_BY_ID = getattr(settings, 'ORM_CACHE_FETCH_BY_ID', False)
DEFAULT_CACHE_TIMEOUT = getattr(settings, 'ORM_CACHE_DEFAULT_TIMEOUT', 60) 
DEFAULT_CACHE_ENABLED = getattr(settings, 'ORM_CACHE_DEFAULT_ENABLED', False)

cache = get_cache()
log = logging.getLogger('orm.cache')


class ObjectCacheMixIn(object):
    cache_fetch_by_id = False
    cache_object_enable = DEFAULT_CACHE_ENABLED
    cache_key_prefix = CACHE_KEY_PREFIX
    cache_timeout = DEFAULT_CACHE_TIMEOUT

    def __init__(self, *args, **kwargs):
        super(ObjectCacheMixIn, self).__init__(*args, **kwargs)

        orm_meta = getattr(self.model, '_orm_meta', None)
        if not orm_meta:
            return

        options = getattr(orm_meta, 'options', None)
        if not options:
            return

        self.cache_object_enable = options['cache_object']
        self.cache_timeout = options['default_timeout']

    def _clone(self, klass=None, **kwargs):
        qs = super(ObjectCacheMixIn, self)._clone(klass, **kwargs)
        qs.cache_fetch_by_id = self.cache_fetch_by_id
        qs.cache_object_enable = self.cache_object_enable
        qs.cache_timeout = self.cache_timeout
        return qs

    def cache(self, timeout=None):
        if self.cache_object_enable:
            if timeout:
                qs = self._clone()
                qs.cache_timeout = timeout
                return qs

            return self

        if not timeout:
            timeout = self.cache_timeout

        qs = self._clone()
        qs.cache_object_enable = True
        qs.cache_timeout = timeout
        return qs

    def no_cache(self):
        if not self.cache_object_enable:
            return self

        qs = self._clone()
        qs.cache_fetch_by_id = qs.cache_object_enable = False
        return qs

    def byid(self):
        if self.cache_fetch_by_id:
            return self

        qs = self._clone()
        qs.cache_fetch_by_id = qs.cache_object_enable = True
        return qs

    def get(self, *args, **kwargs):
        if not self.cache_object_enable or len(args) > 0:
            return super(ObjectCacheMixIn, self).get(*args, **kwargs)
        
        pk, params, obj = None, copy.deepcopy(kwargs), None
        if "pk" in params:
            pk = params.pop('pk')
        elif "id" in kwargs:
            pk = params.pop('id')

        if not pk:
            return super(ObjectCacheMixIn, self).get(*args, **kwargs)

        ckey = get_cache_key_for_pk(self.model, pk, **params)
        obj = cache.get(ckey)
        if not obj:
            obj = super(ObjectCacheMixIn, self).get(*args, **kwargs)
            cache.set(ckey, obj, self.cache_timeout)
            log.info("Orm cache missing: %s(%s)",
                self.model.__name__, obj.id)
        else:
            log.info("Orm cache hit: %s(%s)",
                self.model.__name__, obj.id)
        return obj

    def _get_objects_for_keys(self, model, keys):
        results = cache.get_many([get_cache_key_for_pk(model, k) for k in keys]).values()

        # Now we need to compute which keys weren't present in the cache
        result_ids = [obj.id for obj in results]
        missing = [key for key in keys if key not in result_ids]

        log.info("Orm cache queryset missing objects: %s(%s)",
            self.model.__name__, missing)

        results = list(results)
        objects = model._base_manager.filter(pk__in=missing)
        
        if objects:
            cache.set_many(dict([(obj.cache_key, obj) \
                for obj in objects]), self.cache_timeout)
        
        results.extend(objects)

        #cnt = len(missing) - len(objects)
        #if cnt:
        #    raise CacheMissingWarning("%d objects missing in the database" % (cnt,))

        return results
    
    def fetch_by_id(self):
        values = self.values_list('pk', *self.query.extra.keys())
        ids = [val[0] for val in values]

        keys = dict((get_cache_key_for_pk(self.model, i), i) for i in ids)
        cached = dict((k, v) for k, v in cache.get_many(keys).items() if v is not None)
        missed = [pk for key, pk in keys.iteritems() if key not in cached]

        new = {}
        if missed:
            objects = self.model._base_manager.filter(pk__in=missed)
            new = dict((get_cache_key_for_pk(self.model, o.pk), o) \
                                                    for o in objects)
            cache.set_many(new)
        
        # TODO: improve this for performance issues
        objects = dict((o.pk, o) for o in cached.values() + new.values())
        for pk in ids:
            yield objects[pk]

    def iterator(self):
        if self.cache_fetch_by_id:
            return self.fetch_by_id()

        return super(ObjectCacheMixIn, self).iterator()


class CachedQuerySet(ObjectCacheMixIn, QuerySet):
    pass
