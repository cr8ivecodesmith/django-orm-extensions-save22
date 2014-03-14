# -*- coding: utf-8 -*-


class CacheManagerMixIn(object):
    """
    Base django-orm manager mixin with cache functionality methods.
    """

    def cache(self, *args, **kwargs):
        """ 
        Active cache for this queryset 
        """
        queryset = self.get_query_set()
        cache_method = getattr(queryset, 'cache', None)
        if cache_method:
            return cache_method(*args, **kwargs)

        return queryset

    def no_cache(self, *args, **kwargs):
        """
        Deactive cache for this queryset. 
        """
        queryset = self.get_query_set()
        cache_method = getattr(queryset, 'no_cache', None)
        if cache_method:
            return cache_method(*args, **kwargs)
        return queryset

    def contribute_to_class(self, model, name):
        if hasattr(model, '_orm_meta') and model._orm_meta.options['cache_object']:
            signals.post_save.connect(invalidate_object, sender=model)
            signals.post_delete.connect(invalidate_object, sender=model)
        super(CacheManagerMixIn, self).contribute_to_class(model, name)
