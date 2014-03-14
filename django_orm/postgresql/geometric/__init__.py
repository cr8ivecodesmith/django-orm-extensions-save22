# -*- coding: utf-8 -*-

def register_geometric_types(connection):
    from . import objects

    for objectname in objects.__all__:
        obj_class = getattr(objects, objectname)
        obj_class.register_cast(connection)
        obj_class.register_adapter()
        print "Registering:", obj_class.__name__


from django_orm.dispatch import on_connection_created
on_connection_created.add_single_execution_handler(register_geometric_types)
