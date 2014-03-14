# -*- coding: utf-8 -*-

from django_orm.postgresql.fts.manager import SearchManagerMixIn
from django_orm.postgresql.manager import ManagerMixIn
from django_orm.cache.manager import CacheManagerMixIn
from django.contrib.gis.db import manager

from .queryset import GeoQuerySet

class GeoManager(ManagerMixIn, CacheManagerMixIn, manager.GeoManager):
    use_for_related_fields = True

    def get_query_set(self):
        return GeoQuerySet(model=self.model, using=self._db)


class FtsGeoManager(SearchManagerMixIn, GeoManager):
    use_for_related_fields = True
