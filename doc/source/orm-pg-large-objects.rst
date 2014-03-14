========================
PostgreSQL Large objects
========================

PostgreSQL has a large object facility, which provides stream-style access to user data that 
is stored in a special large-object structure. It is a wrapper for a large object interface.

--------------------------
Example model declaration:
--------------------------

This is a simple example of a model that contains a ``LargeObjectField``. Really this field is a ``oid`` type
field, and it has similar behavior to an integer.

.. code-block:: python

    from django.db import models
    from django_orm.postgresql.fields.bytea import LargeObjectField, LargeObjectProxy
    from django_orm.manager import Manager

    class LargeObjectModel(models.Model):
        lobj = LargeObjectField(default=None, null=True)
        objects = Manager()


------------------------
Creating sample objects:
------------------------

As we are working with files, the behavior is identical to them.

.. code-block:: python
    
    import io

    lobj = LargeObjectProxy()
    lobj.open(mode="wb", using='default')
    
    with io.open("some-file.png", "rb") as f:
        lobj.write(f.read())
        lobj.close()

    instance = LargeObjectModel(lobj=lobj)
    instance.save()


To read the object, is just as much as we read of a regular file.

.. code-block:: python
    
    instance = LargeObjectModel.objects.get(pk=1)
    
    instance.lobj.open("rb")
    with io.open("some-other-file.png", "wb") as f:
        f.write(instance.lobj.read())

    instance.lobj.close()
