django-orm-extensions
=====================

Advanced improvement of django orm with third-party modules in one complete orm subclass.

Due to that there are lots of different "plugins" to use different parts of databases are not covered by the standard orm. 
In reality this is not the problem! The problem arises when you need to use multiple orm plugins at once, and that's where 
you can not import and use!

My main motivation in creating this project is to see to unify several "plugins" in one package, so it can be used 
independently if you want one or more of them.

I certainly do not want to take all the credit, because not all the work i have done, however if you'll take care of having 
a single integrated package with a stable api and covers the most popular databases: postgresql, mysql and sqlite3.


Summary of characteristics
--------------------------

**Supported backends:**

* PostgreSQL 9.x
* MySQL 5.1+
* Sqlite3

In versions before 3.x, it was necessary to have a specific subclass of database backend. Currently all works with the standard 
Django database backends.

**Generic features (All backends):**

* Simple ORM level cache.
* New, more simple and powerfull annotations functions. (under development)
* Advanced filters with custom sql expressions. (under development)
* Database connection hooks.
* Additional indexes attached to model. (pending refactor)

**PostgreSQL specific features:**

* Improved Hstore module.
* Full Text Search integration.
* Server side cursors.
* Large Objects

Documentation index:
--------------------

.. toctree::
   :maxdepth: 1
   
   orm-functions.rst
   orm-expressions.rst
   orm-cache.rst
   orm-indexes.rst


Postgresql specific documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1

   orm-pg-hstore.rst
   orm-pg-fulltext.rst
   orm-pg-server-cursors.rst
   orm-pg-bytea-field.rst
   orm-pg-array-field.rst
   orm-pg-large-objects.rst
