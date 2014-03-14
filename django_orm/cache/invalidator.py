# -*- coding: utf-8 -*-

from django_orm.cache.utils import get_cache
from django_orm.cache.utils import get_cache_key_for_pk
import logging; log = logging.getLogger('orm.cache')

cache = get_cache()

def invalidate_object(instance, **kwargs):
    if not hasattr(instance, 'cache_key'):
        return

    cache.delete(instance.cache_key)
