# -*- coding: utf-8 -*-

from django.contrib.gis.db.models.query import GeoQuerySet as BaseGeoQuerySet
from django_orm.cache.queryset import ObjectCacheMixIn

class GeoQuerySet(ObjectCacheMixIn, BaseGeoQuerySet):
    pass
