=================
PostgreSQL HStore
=================

Hstore is a niche library which integrates the `hstore`_ extension of PostgreSQL into Django,
assuming one is using Django 1.3+, PostgreSQL 9.0+, and Psycopg 2.4+.

Limitations and notes
---------------------

- PostgreSQL's implementation of hstore has no concept of type; it stores a mapping of string keys to
  string values. This library makes no attempt to coerce keys or values to strings.


Note to postgresql 9.0 users: 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If using postgresql9.0 must manually install the extension hstore to create the database 
or make hstore already installed in the corresponding template. For an example, you can see the file "runtests-pg90".


Note to South users:
^^^^^^^^^^^^^^^^^^^^

If you keep getting errors like `There is no South database module 'south.db.None' for your database.`, add the following to `settings.py`:

.. code-block:: python

    SOUTH_DATABASE_ADAPTERS = {'default': 'south.db.postgresql_psycopg2'}


Classes
-------

The library provides three principal classes:

``django_orm.postgresql.hstore.DictionaryField``
    An ORM field which stores a mapping of string key/value pairs in an hstore column.
``django_orm.postgresql.hstore.ReferencesField``
    An ORM field which builds on DictionaryField to store a mapping of string keys to
    django object references, much like ForeignKey.
``django_orm.postgresql.hstore.HStoreManager``
    An ORM manager which provides much of the query functionality of the library.


Example of model declaration:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from django.db import models
    from django_orm.postgresql import hstore

    class Something(models.Model):
        name = models.CharField(max_length=32)
        data = hstore.DictionaryField(db_index=True)
        objects = hstore.HStoreManager()

        def __unicode__(self):
            return self.name


You then treat the ``data`` field as simply a dictionary of string pairs:

.. code-block:: python

    instance = Something.objects.create(name='something', data={'a': '1', 'b': '2'})
    assert instance.data['a'] == '1'

    empty = Something.objects.create(name='empty')
    assert empty.data == {}

    empty.data['a'] = '1'
    empty.save()
    assert Something.objects.get(name='something').data['a'] == '1'


You can issue indexed queries against hstore fields:


.. code-block:: python

    from django_orm.postgresql.hstore.expressions import HstoreExpression as HE

    # equivalence
    Something.objects.filter(data={'a': '1', 'b': '2'})

    # subset by key/value mapping
    Something.objects.where(HE("data").contains({'a':'1'}))

    # subset by list of keys
    Something.objects.where(HE("data").contains(['a', 'b']))

    # subset by single key
    Something.objects.where(HE("data").contains("a"))


You can also take advantage of some db-side functionality by using the manager:

.. code-block:: python

    # identify the keys present in an hstore field
    >>> Something.objects.filter(id=1).hkeys(attr='data')
    ['a', 'b']

    # peek at a a named value within an hstore field
    >>> Something.objects.filter(id=1).hpeek(attr='data', key='a')
    '1'

    # remove a key/value pair from an hstore field
    >>> Something.objects.filter(name='something').hremove('data', 'b')


In addition to filters and specific methods to retrieve keys or hstore field values, 
we can also use annotations, and then we can filter for them.

.. code-block:: python

    from django_orm.postgresql.hstore.functions import HstoreSlice, HstorePeek, HstoreKeysç

    queryset = SomeModel.objects.annotate_functions(
        sliced = HstoreSlice("hstorefield", ['v']),
        peeked = HstorePeek("hstorefield", "v"),
        keys = HstoreKeys("hstorefield"),
    )
