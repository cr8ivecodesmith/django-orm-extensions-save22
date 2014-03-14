# -*- coding: utf-8 -*-

class ManagerMixIn(object):
    """
    Base django-orm manager mixin.
    """
    def contribute_to_class(self, model, name):
        if not getattr(model, '_orm_manager', None):
            model._orm_manager = self
        super(ManagerMixIn, self).contribute_to_class(model, name)

    def annotate_functions(self, **kwargs):
        return self.get_query_set().annotate_functions(**kwargs)

    def where(self, *args):
        return self.get_query_set().where(*args)
