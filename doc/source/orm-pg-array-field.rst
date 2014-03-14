==============================
PostgreSQL arrays (ArrayField)
==============================

This is a field that represents native postgresql array. It can be of type integer and type text, but not limited to these.

Types supported:
^^^^^^^^^^^^^^^^

- **int** (int[])
- **text** (text[])
- **double precision** (double precision[])
- **real** (real[])
- **varchar(N)** (varchar(N)[])

Usage in model declaration:
---------------------------

.. code-block:: python

    from django.db import models
    from django_orm.postgresql.fields.arrays import ArrayField
    from django_orm.manager import Manager

    class TestModel(models.Model):
        my_int_list = ArrayField(dbtype='int', null=True)
        my_text_list = ArrayField(dbtype='text', null=True)
        objects = Manager()


Creating sample objects:
------------------------

.. code-block:: python

    >>> TestModel.objects.create(
    ...     my_int_list = [1,2,3,4],
    ...     my_text_list = ['Hello', 'World'],
    ...     my_varchar_list = ['foo', 'bar']
    ... )
    <TestModel: TestModel object>

    >>> TestModel.objects.create(
    ...     my_int_list = [5,6,7,8,9],
    ...     my_text_list = ['Goodbye', 'World'],
    ...     my_varchar_list = ['door', 'window']
    ... )


Generated SQL for this create sentences:

.. code-block:: sql
    
    INSERT INTO "testapp_testmodel" 
        ("my_int_list", "my_text_list", "my_varchar_list") 
        VALUES (
            ARRAY[1, 2, 3, 4], 
            ARRAY['Hello', 'World'], 
            ARRAY['foo', 'bar']
        ) 
        RETURNING "testapp_testmodel"."id";

    INSERT INTO "testapp_testmodel" 
        ("my_int_list", "my_text_list", "my_varchar_list") 
        VALUES (
            ARRAY[5, 6, 7, 8, 9], 
            ARRAY['Goodbye', 'World'], 
            ARRAY['door', 'window']
        ) 
        RETURNING "testapp_testmodel"."id"; 


Builtins sql functions for array fields.
----------------------------------------

TODO


Builtins sql expressions for array fields.
------------------------------------------

TODO
