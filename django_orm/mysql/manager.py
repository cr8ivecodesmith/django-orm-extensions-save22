# -*- coding: utf-8 -*-

from django.db import models
from django_orm.mysql.queryset import MyQuerySet
from django_orm.cache.manager import CacheManagerMixIn
from django_orm.core.manager import ManagerMixIn


class Manager(ManagerMixIn, CacheManagerMixIn, models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return MyQuerySet(model=self.model, using=self._db)
