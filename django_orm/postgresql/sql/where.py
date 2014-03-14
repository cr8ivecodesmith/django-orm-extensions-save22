# -*- coding: utf-8 -*-

from django import VERSION
from django.db.models.query import QuerySet
from django.db.models.sql.constants import SINGLE
from django.db.models.sql.datastructures import EmptyResultSet
from django.db.models.sql.query import Query
from django.db.models.sql.subqueries import UpdateQuery
from django.db.models.sql.where import EmptyShortCircuit, WhereNode
from django.utils.encoding import force_unicode

try:
    from django.db.models.sql.where import QueryWrapper # django <= 1.3
except ImportError:
    from django.db.models.query_utils import QueryWrapper # django >= 1.4

from django_orm.postgresql.constants import QUERY_TERMS, FTS_LOCKUPS
from django_orm.postgresql.constants import GEOMETRIC_LOOKUPS, VARCHAR_LOOKUPS
from django_orm.postgresql.constants import GEOMETRIC_TYPES
from django_orm.postgresql.hstore.query import select_query, update_query
from django_orm.cache.query import CachedQuerySet
from django_orm.postgresql.composite import C

lookups = {
    'is_closed': lambda field, param: ('isclosed(%s) = %%s' % field, [param]),
    'is_open': lambda field, param: ('isclosed(%s) = %%s' % field, [param]),
    'area': lambda field, param: ('area(%s) = %%s' % field, [param]),
    'area_gt': lambda field, param: ('area(%s) > %%s' % field, [param]),
    'area_lt': lambda field, param: ('area(%s) < %%s' % field, [param]),
    'area_gte': lambda field, param: ('area(%s) >= %%s' % field, [param]),
    'area_lte': lambda field, param: ('area(%s) <= %%s' % field, [param]),
    'diameter': lambda field, param: ('diameter(%s) = %%s' % field, [param]),
    'diameter_gt': lambda field, param: ('diameter(%s) > %%s' % field, [param]),
    'diameter_lt': lambda field, param: ('diameter(%s) < %%s' % field, [param]),
    'diameter_gte': lambda field, param: ('diameter(%s) >= %%s' % field, [param]),
    'diameter_lte': lambda field, param: ('diameter(%s) <= %%s' % field, [param]),
    'length': lambda field, param: ('length(%s) = %%s' % field, [param]),
    'length_gt': lambda field, param: ('length(%s) > %%s' % field, [param]),
    'length_lt': lambda field, param: ('length(%s) < %%s' % field, [param]),
    'length_gte': lambda field, param: ('length(%s) >= %%s' % field, [param]),
    'length_lte': lambda field, param: ('length(%s) <= %%s' % field, [param]),
    'width': lambda field, param: ('width(%s) = %%s' % field, [param]),
    'width_gt': lambda field, param: ('width(%s) > %%s' % field, [param]),
    'width_lt': lambda field, param: ('width(%s) < %%s' % field, [param]),
    'width_gte': lambda field, param: ('width(%s) >= %%s' % field, [param]),
    'width_lte': lambda field, param: ('width(%s) <= %%s' % field, [param]),
    'npoints': lambda field, param: ('npoints(%s) = %%s' % field, [param]),
    'npoints_gt': lambda field, param: ('npoints(%s) > %%s' % field, [param]),
    'npoints_lt': lambda field, param: ('npoints(%s) < %%s' % field, [param]),
    'npoints_gte': lambda field, param: ('npoints(%s) >= %%s' % field, [param]),
    'npoints_lte': lambda field, param: ('npoints(%s) <= %%s' % field, [param]),
    'overlap': lambda field, param: ('%s && %%s' % field, [param]),
    'strictly_left_of': lambda field, param: ('%s << %%s' % field, [param]),
    'strictly_right_of': lambda field, param: ('%s >> %%s' % field, [param]),
    'strictly_below': lambda field, param: ('%s <<| %%s' % field, [param]),
    'strictly_above': lambda field, param: ('%s |>> %%s' % field, [param]),
    'notextendto_right_of': lambda field, param: ('%s &< %%s' % field, [param]),
    'notextendto_left_of': lambda field, param: ('%s &> %%s' % field, [param]),
    'notextend_above': lambda field, param: ('%s &<| %%s' % field, [param]),
    'notextend_below': lambda field, param: ('%s |&> %%s' % field, [param]),
    'intersects': lambda field, param: ('%s ?# %%s' % field, [param]),
    'is_horizontal': lambda field, param: ('(?- %s) = %%s' % field, [param]),
    'is_perpendicular': lambda field, param: ('%s ?-| %%s' % field, [param]),
    'is_parallel': lambda field, param: ('%s ?|| %%s' % field, [param]),
    'same_as': lambda field, param: ('%s ~= %%s' % field, [param]),
    'indexexact': lambda field, param: ('%s[%s] = %%s' % (field, param[0]+1), [param[1]]),
    'distinct': lambda field, param: ('%s <> %%s' % field, [param]),
    'containedby': lambda field, param: ('%s <@ %%s' % field, [param]),
    'unaccent': lambda field, param: ('unaccent(%s) LIKE unaccent(%%s)' % field, [param]),
    'iunaccent': lambda field, param: ('lower(unaccent(%s)) LIKE lower(unaccent(%%s))' %\
        field, [param]),

    'center': lambda field, param: ('@@ %s ~= %%s' % field, [param]),
    'numpoints': lambda field, param: ('# %s = %%s' % field, [param]),
    'numpoints_gt': lambda field, param: ('# %s > %%s' % field, [param]),
    'numpoints_lt': lambda field, param: ('# %s < %%s' % field, [param]),
    'numpoints_gte': lambda field, param: ('# %s >= %%s' % field, [param]),
    'numpoints_lte': lambda field, param: ('# %s <= %%s' % field, [param]),

    'contains': lambda field, param, is_list: ('%s @> %%s' % field, [param]) \
        if is_list else (u'%%s = ANY(%s)' % field, [param]),
    'distance': lambda field, param: ('%s <-> %%s = %s' % (field, param[1]), [param[0]]),
}
