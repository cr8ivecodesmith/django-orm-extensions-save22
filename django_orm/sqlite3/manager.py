# -*- coding: utf-8 -*-

from django.db import models
from django_orm.sqlite3.queryset import SqliteQuerySet
from django_orm.cache.manager import CacheManagerMixIn
from django_orm.core.manager import ManagerMixIn


class Manager(ManagerMixIn, CacheManagerMixIn, models.Manager):
    use_for_related_fields = True
    
    def get_query_set(self):
        return SqliteQuerySet(model=self.model, using=self._db)

    def add_unaccent_filter(self, *args, **kwargs):
        """
        Very experimental method.
        """
        return self.get_query_set().add_unaccent_filter(*args, **kwargs)
