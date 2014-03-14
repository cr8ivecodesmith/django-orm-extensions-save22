from django.db import models
from django_orm.postgresql.hstore.queryset import HStoreQuerySet
from django_orm.postgresql.manager import Manager

class HStoreManager(Manager):
    """
    Object manager which enables hstore features.
    """
    use_for_related_fields = True

    def get_query_set(self):
        return HStoreQuerySet(self.model, using=self._db)

    def hkeys(self, attr):
        return self.get_query_set().hkeys(attr)

    def hpeek(self, attr, key):
        return self.get_query_set().hpeek(attr, key)

    def hslice(self, attr, keys, **params):
        return self.get_query_set().hslice(attr, keys)

