# -*- coding: utf-8 -*-

import re
from django.utils import simplejson as json
from django.db import connection
from psycopg2.extensions import adapt, register_adapter, AsIs, new_type, register_type

from .adapt import ADAPT_MAPPER

rx_circle_float = re.compile(r'<\(([\d\.\-]*),([\d\.\-]*)\),([\d\.\-]*)>')
rx_line = re.compile(r'\[\(([\d\.\-]*),\s*([\w\.\-]*)\),\s*\(([\d\.\-]*),\s*([\d\.\+]*)\)\]')
rx_point = re.compile(r'\(([\d\.\-]*),\s*([\d\.\-]*)\)')
rx_box = re.compile(r'\(([\d\.\-]*),\s*([\d\.\-]*)\),\s*\(([\d\.\-]*),\s*([\d\.\-]*)\)')
rx_path_identify = re.compile(r'^((?:\(|\[))(.*)(?:\)|\])$')

""" SQL->PYTHON CAST """

def cast_point(value, cur):
    if value is None:
        return None

    res = rx_point.search(value)
    if not res:
        raise ValueError("bad point representation: %r" % value)
    
    return Point([int(x) if "." not in x else float(x) \
        for x in res.groups()])


def cast_circle(value, cur):
    if value is None:
        return None

    rxres = rx_circle_float.search(value)
    if not rxres:
        raise ValueError("bad circle representation: %r" % value)

    return Circle([int(x) if "." not in x else float(x) \
        for x in rxres.groups()])

def cast_lseg(value, cur):
    if value is None:
        return None

    rxres = rx_line.search(value)
    if not rxres:
        raise ValueError("bad lseg representation: %r" % value)

    return Lseg([int(x) if "." not in x else float(x) \
        for x in rxres.groups()])

def cast_box(value, cur):
    if value is None:
        return None
    
    rxres = rx_box.search(value)
    if not rxres:
        raise ValueError("bad box representation: %r" % value)

    return Box([int(x) if "." not in x else float(x) \
        for x in rxres.groups()])

def cast_path(value, cur):
    if value is None:
        return None

    ident = rx_path_identify.search(value)
    if not ident:
        raise ValueError("bad path representation: %r" % value)

    is_closed = True if "(" == ident.group(1) else False
    points = ident.group(2)
    if not points.strip():
        raise ValueError("bad path representation: %r" % value)
    
    return Path([(
        int(x) if "." not in x else float(x), \
        int(y) if "." not in y else float(y) \
    ) for x, y in rx_point.findall(points)], closed=is_closed)

def cast_polygon(value, cur):
    if value is None:
        return None

    ident = rx_path_identify.search(value)
    if not ident:
        raise ValueError("bad path representation: %r" % value)

    is_closed = True if "(" == ident.group(1) else False
    points = ident.group(2)
    if not points.strip():
        raise ValueError("bad path representation: %r" % value)
    
    return Polygon([(
        int(x) if "." not in x else float(x), \
        int(y) if "." not in y else float(y) \
    ) for x, y in rx_point.findall(points)], closed=is_closed)


CAST_MAPPER = {
    'Point': cast_point,
    'Circle': cast_circle,
    'Box': cast_box,
    'Path': cast_path,
    'Polygon': cast_polygon,
    'Lseg': cast_lseg,
}


class GeometricMeta(type):
    """
    Base meta class for all geometryc types.
    """

    def __init__(cls, name, bases, attrs):
        super(GeometricMeta, cls).__init__(name, bases, attrs)
        cls._registed = False

    def __call__(cls, *args):
        if len(args) > 1:
            return super(GeometricMeta, cls).__call__(tuple(args))
        elif isinstance(args[0], (list, tuple)):
            return super(GeometricMeta, cls).__call__(*args)
        raise ValueError("Incorrect parameters")
        
        # old code: register on demand.
        #if cls.type_name() not in ADAPT_MAPPER:
        #    cls._registed = True
        #    return instance

        #cls.register_adapter()
        #GeometricMeta.__call__ = super(GeometricMeta, cls).__call__
        return instance

    def register_cast(cls, connection):
        cast_function = CAST_MAPPER[cls.type_name()]
        cursor = connection.cursor()
        cursor.execute(cls.sql_for_oid())
        oid = cursor.description[0][1]
        cursor.close()

        PGTYPE = new_type((oid,), cls.type_name().upper(), cast_function)
        register_type(PGTYPE)

    def register_adapter(cls):
        adapt_function = ADAPT_MAPPER[cls.type_name()]
        register_adapter(cls, adapt_function)

    def type_name(cls):
        return cls.__name__

    def db_type(cls, connection):
        return cls.type_name().lower()

    def sql_for_oid(cls):
        ntype = cls.type_name().lower()
        return "SELECT NULL::%s" % (ntype)


class Point(tuple):
    """ 
    Class that rep resents of geometric point. 
    """
    __metaclass__ = GeometricMeta

    def __init__(self, args):
        if len(args) == 2:
            super(Point, self).__init__(args)
        else: 
            raise ValueError("Max is 2 elements")
        self._validate()


    def _validate(self):
        if not isinstance(self.x, (int, long, float)) \
            or not isinstance(self.y, (int, long, float)):
            raise ValueError("invalid data")

    def __repr__(self):
        return "<Point(%s,%s)>" % self

    @property
    def x(self):
        return self[0]
    
    @property
    def y(self):
        return self[1]


class Circle(tuple):
    __metaclass__ = GeometricMeta
    def __init__(self, args):
        if len(args) == 3:
            super(Circle, self).__init__(args)
        else:
            raise ValueError("invalid data")
        self._validate()

    def _validate(self):
        if not isinstance(self.r, (int, long, float)):
            raise ValueError("invalid data")

    def __repr__(self):
        return "<Circle(%s,%s)>" % (self.point, self.r)

    @property
    def r(self):
        return self[2]

    @property
    def point(self):
        return Point(self[:-1])

    def to_box(self):
        if hasattr(self, '_box'):
            return self._box

        cur = connection.cursor()
        cur.execute("select box(%s) as _;", [self])
        res = cur.fetchone()
        cur.close()

        if not res:
            raise ValueError("Unexpected error")

        self._box = res[0]
        return res[0]


class Lseg(tuple):
    __metaclass__ = GeometricMeta

    def __init__(self, args):
        if len(args) == 4:
            super(Lseg, self).__init__(args)
        else:
            raise ValueError("invalid content")

    def __iter__(self):
        yield tuple(self.init_point)
        yield tuple(self.end_point)

    def __repr__(self):
        return "<Lseg(%s, %s)>" % \
            (self.init_point, self.end_point)

    @property
    def init_point(self):
        return Point(self[:2])

    @property
    def end_point(self):
        return Point(self[2:])


class Box(tuple):
    __metaclass__ = GeometricMeta
    def __init__(self, args):
        if len(args) == 4:
            super(Box, self).__init__(args)
        else:
            raise ValueError("invalid content")

    def __repr__(self):
        return "<Box(%s,%s),(%s,%s)>" % self

    @property
    def init_point(self):
        return Point(self[:2])

    @property
    def end_point(self):
        return Point(self[2:])

    @property
    def center_point(self):
        if hasattr(self, '_center_point'):
            return self._center_point

        cur = connection.cursor()
        cur.execute("select @@ %s;", [self])
        res = cur.fetchone()
        cur.close()

        if not res:
            raise ValueError("Unexpected error")

        self._center_point = res[0]
        return res[0]


class Path(tuple):
    __metaclass__ = GeometricMeta
    closed = False

    def __init__(self, args):
        points = []
        for item in args:
            if isinstance(item, (tuple, list, Point)):
                points.append(tuple(item))
            else:
                points = []
                raise ValueError("invalid content")
        
        self.closed = isinstance(args, tuple)

        if len(points) == 0:
            raise ValueError("invalid content")

        super(Path, self).__init__(points)
    
    def __repr__(self):
        return "<Path(%s) closed=%s>" % (len(self), self.closed)


class Polygon(Path):
    __metaclass__ = GeometricMeta

    def __repr__(self):
        return "<Polygon(%s) closed=%s>" % (len(self), self.closed)


__all__ = ['Polygon', 'Point', 'Box', 'Circle', 'Path', 'Lseg']
