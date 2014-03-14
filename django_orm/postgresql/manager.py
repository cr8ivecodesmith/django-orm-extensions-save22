# -*- coding: utf-8 -*-

from django_orm.postgresql.fulltext.manager import SearchManagerMixIn
from django_orm.postgresql.queryset import PgQuerySet
from django_orm.cache.manager import CacheManagerMixIn
from django_orm.core.manager import ManagerMixIn
from django.db import models


class Manager(ManagerMixIn, CacheManagerMixIn, models.Manager):
    """
    Normal user manager. With cache methods.
    Without fulltext search functionality.
    """
    use_for_related_fields = True

    def get_query_set(self):
        return PgQuerySet(model=self.model, using=self._db)


class FtsManager(SearchManagerMixIn, Manager):
    """
    Base django-orm manager with full text search methods.
    """
    use_for_related_fields = True


#class ArrayDataMixin(object):
#    def get_query_set(self):
#        # TODO: this is invalid queryset
#        return PgQuerySet(model=self.model, using=self._db)
#
#    def array_slice(self, attr, x, y, **params):
#        """
#        Deactive cache for this queryset. 
#        """
#        return self.filter(**params).array_slice(attr, x, y)
#
#    def array_length(self, attr, **params):
#        """
#        Get length from some array field. Only for postgresql vendor. 
#        """
#        return self.filter(**params).array_length(attr)
#
#
#class ArrayManager(ArrayDataMixin, Manager):
#    """
#    Django-orm base manager for use with array fields.
#    """
#    use_for_related_fields = True

