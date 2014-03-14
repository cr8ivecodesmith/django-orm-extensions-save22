=============
Sql Functions
=============

By default, the django orm annotations only supports predefined types that return integers or float. 
To solve this problem, **django-orm** introduces a new feature available in the manager and queryset: ``annotate_functions()`` 
and a ``django_orm.core.sql.SqlFunction`` class that may define their own functions and use them.

For example, we take ``bit_length(text)`` postgresql function, and create django function definition:

.. code-block:: python
    
    from django_orm.core.sql import SqlFunction

    class BitLength(SqlFunction):
        sql_function = "bit_length"


To use it is pretty simple, we take a model, we add the django-orm manager and do the query like this:

.. code-block:: python

    from django_orm.postgresql.manager import Manager
    from django.db import models

    class Person(models.Model):
        name = models.CharField(max_length=200)

        objects = models.Manager()
        manager = Manager()

    queryset = Person.manager.annotate_functions(
        bitlength=BitLength("name")
    )


This works like annotate but more flexible and supports all db types that yo defined or registred.

.. By default, has incorporated many functions predefined and available in different databases:
    TODO:
