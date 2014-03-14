# -*- coding: utf-8 -*-

from django.db import connection
from django.test import TestCase
from django.utils import unittest

from django_orm.postgresql.aggregates import Unaccent
from django_orm.postgresql.geometric.objects import *

from .models import IntModel, TextModel, DoubleModel, VarcharModel
from .models import ByteaModel, IntervalModel, GeomModel
from .models import Foo2Model, FooModel, FooBigModel
from .composite_types import Person, Account

from django_orm.postgresql.composite import C

#class CompositeTypesSimpleTest(TestCase):
#    def setUp(self):
#        self.o1 = FooModel.objects.create(
#            person = Person(name="Andrei Antoukh", age=23)
#        )
#        self.o2 = FooModel.objects.create(
#            person = Person(name="Francisco", age=14)
#        )
#
#    def tearDown(self):
#        self.o1.delete()
#        self.o2.delete()
#
#    def test_simple_get(self):
#        p1 = FooModel.objects.get(pk=self.o1.id)
#        self.assertIsInstance(p1.person, Person)
#        self.assertEqual(p1.person.name, u"Andrei Antoukh")
#
#    def test_simple_save(self):
#        self.o1.person.name = u"Carlos"
#        self.o1.save()
#
#        p1 = FooModel.objects.get(pk=self.o1.id)
#        self.assertEqual(p1.person.name, u"Carlos")
#
#    def test_simple_query(self):
#        qs = FooModel.objects.filter(
#            person=C("(person).name = ?", u'Andrei Antoukh')
#        )
#        self.assertEqual(len(qs), 1)
#
#    def test_like_query(self):
#        qs = FooModel.objects.filter(
#            person=C("(person).name ILIKE ?", u'%andrei%')
#        )
#        self.assertEqual(len(qs), 1)
#
#    def test_unaccent_query(self):
#        qs = FooModel.objects.filter(
#            person=C(u"(person).name UNACCENT ?", u'%Andréi%')
#        )
#        self.assertEqual(len(qs), 1)

    
class DoublePrecisionArrayFieldTest(TestCase):
    def setUp(self):
        DoubleModel.objects.all().delete()
        self.p1 = DoubleModel.objects.create(lista=[1.2,2.3,3.4,4.5,5.6])
        self.p2 = DoubleModel.objects.create(lista=[11.5,44.3,22.1])
        self.p3 = DoubleModel.objects.create(lista=[5.1,3.2,6.3,7.4])
    
    def test_double_array_contains(self):
        qs = DoubleModel.objects.filter(lista__contains=1.2)
        self.assertEqual(qs.count(), 1)

    def test_double_array_overlap(self):
        qs = DoubleModel.objects.filter(lista__overlap=[1.2,11.5])
        self.assertEqual(qs.count(), 2)

    def test_double_array_distinct(self):
        qs = DoubleModel.objects.filter(lista__distinct=[11.5,44.3,22.1])
        self.assertEqual(qs.count(), 2)

    def test_double_array_length(self):
        length = DoubleModel.objects.filter(id=self.p1.id).array_length(attr='lista')
        self.assertEqual(length, 5)

    def test_double_array_slice(self):
        result = DoubleModel.objects.filter(id=self.p1.id).array_slice('lista', 1,2)
        self.assertEqual(result, [2.3,3.4])

    def test_double_array_aggregates_length(self):
        from django_orm.postgresql.aggregates import ArrayLength

        qs = DoubleModel.objects.annotate(lista_length=ArrayLength('lista')).order_by('id')
        self.assertEqual(qs[0].lista_length, 5.0)
    
    def test_double_array_aggregates_length_sum(self):
        from django_orm.postgresql.aggregates import ArrayLength

        result = DoubleModel.objects.aggregate(total_length=ArrayLength('lista', sum=True))
        self.assertEqual(result['total_length'], 12.0)


class IntArrayFieldTest(TestCase):
    def setUp(self):
        IntModel.objects.all().delete()
        self.p1 = IntModel.objects.create(lista=[1,2,3,4,5])
        self.p2 = IntModel.objects.create(lista=[11,22,33,44])
        self.p3 = IntModel.objects.create(lista=[5,3,6,7,8])
        self.p4 = IntModel.objects.create(lista=[3,4,5,6,7,8])
        self.p5 = IntModel.objects.create(lista=[9,10,11,11,10])
        self.p6 = IntModel.objects.create(lista=[1,2,3,4,5])
    
    def test_int_array_indexexact(self):
        qs = IntModel.objects.filter(lista__indexexact=(0,1))
        self.assertEqual(qs.count(), 2)
    
    def test_int_array_contains(self):
        qs = IntModel.objects.filter(lista__contains=1)
        self.assertEqual(qs.count(), 2)

    def test_int_array_contains_list(self):
        qs = IntModel.objects.filter(lista__contains=[1,2])
        self.assertEqual(qs.count(), 2)

    def test_int_array_overlap(self):
        qs = IntModel.objects.filter(lista__overlap=[1,9])
        self.assertEqual(qs.count(), 3)

    def test_int_array_distinct(self):
        qs = IntModel.objects.filter(lista__distinct=[1,2,3,4,5])
        self.assertEqual(qs.count(), 4)

    def test_int_array_length(self):
        length = IntModel.objects.filter(id=self.p1.id).array_length(attr='lista')
        self.assertEqual(length, 5)

    def test_int_array_slice(self):
        result = IntModel.objects.filter(id=self.p1.id).array_slice('lista', 1,3)
        self.assertEqual(result, [2,3,4])

    def test_int_array_aggregates_length(self):
        from django_orm.postgresql.aggregates import ArrayLength

        qs = IntModel.objects.annotate(lista_length=ArrayLength('lista')).order_by('id')
        self.assertEqual(qs[0].lista_length, 5.0)
        self.assertEqual(qs[3].lista_length, 6.0)
    
    def test_int_array_aggregates_length_sum(self):
        from django_orm.postgresql.aggregates import ArrayLength

        result = IntModel.objects.aggregate(total_length=ArrayLength('lista', sum=True))
        self.assertEqual(result['total_length'], 30)

from django.db import connection
from pprint import pprint

class TextArrayFieldTest(TestCase):
    def setUp(self):
        TextModel.objects.all().delete()
        self.p1 = TextModel.objects.create(lista=[u'hola', u'mundo'])
        self.p2 = TextModel.objects.create(lista=[u'hellow', u'world'])
        self.p3 = TextModel.objects.create(lista=[u'привет', u'моя', u'страна'])
    
    def test_text_array_contains(self):
        qs = TextModel.objects.filter(lista__contains=u'mundo')
        self.assertEqual(qs.count(), 1)

        qs = TextModel.objects.filter(lista__contains=u'страна')
        self.assertEqual(qs.count(), 1)

    def test_text_array_overlap(self):
        qs = TextModel.objects.filter(lista__overlap=['hola','world'])
        self.assertEqual(qs.count(), 2)

    def test_text_array_distinct(self):
        qs = TextModel.objects.filter(lista__distinct=['hellow', 'world'])
        self.assertEqual(qs.count(), 2)

    def test_text_array_length(self):
        length = TextModel.objects.filter(id=self.p3.id).array_length(attr='lista')
        self.assertEqual(length, 3)

    def test_text_array_slice(self):
        result = TextModel.objects.filter(id=self.p3.id).array_slice('lista', 0,1)
        self.assertEqual(result, [u'привет', u'моя'])

    def test_text_array_aggregates_length(self):
        from django_orm.postgresql.aggregates import ArrayLength

        qs = TextModel.objects.annotate(lista_length=ArrayLength('lista')).order_by('id')
        self.assertEqual(qs[0].lista_length, 2.0)
        
    def test_text_array_aggregates_length_sum(self):
        from django_orm.postgresql.aggregates import ArrayLength

        result = TextModel.objects.aggregate(total_length=ArrayLength('lista', sum=True))
        self.assertEqual(result['total_length'], 7)



class VarcharArrayFieldTest(TestCase):
    def setUp(self):
        VarcharModel.objects.all().delete()
        self.p1 = VarcharModel.objects.create(lista=['hola', 'mundo'])
        self.p2 = VarcharModel.objects.create(lista=['hellow', 'world'])
        self.p3 = VarcharModel.objects.create(lista=['привет', 'моя', 'страна'])
    
    def test_varchar_array_contains(self):
        qs = VarcharModel.objects.filter(lista__contains='hola')
        self.assertEqual(qs.count(), 1)

        qs = VarcharModel.objects.filter(lista__contains=u'привет')
        self.assertEqual(qs.count(), 1)

    def test_varchar_array_overlap(self):
        qs = VarcharModel.objects.filter(lista__overlap=['hola','world'])
        self.assertEqual(qs.count(), 2)

    def test_varchar_array_distinct(self):
        qs = VarcharModel.objects.filter(lista__distinct=['hellow', 'world'])
        self.assertEqual(qs.count(), 2)

    def test_varchar_array_length(self):
        length = VarcharModel.objects.filter(id=self.p3.id).array_length(attr='lista')
        self.assertEqual(length, 3)
    
    def test_varchar_array_slice(self):
        result = VarcharModel.objects.filter(id=self.p3.id).array_slice('lista', 0,1)
        self.assertEqual(result, [u'привет', u'моя'])

    def test_varchar_array_aggregates_length(self):
        from django_orm.postgresql.aggregates import ArrayLength

        qs = VarcharModel.objects.annotate(lista_length=ArrayLength('lista')).order_by('id')
        self.assertEqual(qs[0].lista_length, 2.0)
        
    def test_varchar_array_aggregates_length_sum(self):
        from django_orm.postgresql.aggregates import ArrayLength
        result = VarcharModel.objects.aggregate(total_length=ArrayLength('lista', sum=True))
        self.assertEqual(result['total_length'], 7)


from datetime import timedelta

class IntervalFieldTest(TestCase):
    def setUp(self):
        IntervalModel.objects.all().delete()
        self.p1 = IntervalModel.objects.create(iv=timedelta(21))
        self.p2 = IntervalModel.objects.create(iv=timedelta(30, 600))

    def test_interval_gt(self):
        qs = IntervalModel.objects.filter(iv__gt=timedelta(22))
        self.assertEqual(qs.count(), 1)

    def test_interval_gte(self):
        qs = IntervalModel.objects.filter(iv__gte=timedelta(30, 600))
        self.assertEqual(qs.count(), 1)

    def test_interval_exact(self):
        qs = IntervalModel.objects.filter(iv=timedelta(21))
        self.assertEqual(qs.count(), 1)

        qs = IntervalModel.objects.filter(iv=timedelta(22))
        self.assertEqual(qs.count(), 0)


import hashlib, os

class ByteaFieldTest(TestCase):
    def setUp(self):
        ByteaModel.objects.all().delete()

    def test_insert(self):
        path = os.path.join(os.path.dirname(__file__), "..", "test.png")
        bindata = ''

        with open(path, "rb") as f:
            bindata = f.read()

        strhash = hashlib.sha256(bindata).hexdigest()
        obj = ByteaModel.objects.create(bb=bindata)
        obj = ByteaModel.objects.get(pk=obj.id)
        self.assertEqual(strhash, hashlib.sha256(obj.bb).hexdigest())


class GeometricFieldsTest(TestCase):
    def setUp(self):
        GeomModel.objects.all().delete()
        print Lseg, type(Lseg)
        self.models = [
            GeomModel.objects.create(
                pt = Point((1,2)),
                #pl = Polygon((1,2), (3,4), (5,6), (-2,4), (1,2)),
                ln = Lseg([1,2,3,4]),
                bx = Box([1,1,4,4]),
                cr = Circle([2,3,5]),
                ph = Path([(1,2),(2,2),(3,2)])
            ),
            GeomModel.objects.create(
                pt = Point((-2,-2)),
                #pl = Polygon((2,2), (3,4), (-5,6), (-2,4), (2,2)),
                ln = Lseg([-4,-4,0,0]),
                bx = Box([1,1,-4,-4]),
                cr = Circle([2,3,3]),
                ph = Path([(1,2),(2,2),(3,2)])
            ),
            GeomModel.objects.create(
                pt = Point((1,2)),
                #pl = Polygon((1,2), (3,4), (5,6), (-2,4), (1,2)),
                ln = Lseg([5,2,3,4]),
                bx = Box([1,3,4,3]),
                cr = Circle([4,5,10]),
                ph = Path([(1,2),(2,2),(1,2)])
            ),
            GeomModel.objects.create(
                bx = Box([0,0,2,2]),
            ),
        ]

    def test_same_as(self):
        qs = GeomModel.objects.filter(
            bx__same_as=Box([1,3,4,3])
        )
        self.assertEqual(qs.count(), 1)
    
    def test_strictly_left(self):
        qs = GeomModel.objects.filter(
            cr__strictly_left_of=Circle([10,5,1])
        )
        self.assertEqual(qs.count(), 2)

    def test_is_horizontal(self):
        qs = GeomModel.objects.filter(
            ln__is_horizontal=False
        )
        self.assertEqual(qs.count(), 3)
    
    def test_area(self):
        qs = GeomModel.objects.filter(
            cr__area_gt=2
        )
        self.assertEqual(qs.count(), 3)
        qs = GeomModel.objects.filter(
            cr__area_lte=3
        )
        self.assertEqual(qs.count(), 0)
    
    def test_overlap(self):
        qs = GeomModel.objects.filter(
            bx__overlap = Box([2,2,6,6])
        )
        self.assertEqual(qs.count(), 3)

    def test_is_closed(self):
        qs = GeomModel.objects.filter(
            ph__is_closed=True
        )
        self.assertEqual(qs.count(), 0)

    def test_is_open(self):
        qs = GeomModel.objects.filter(
            ph__is_open=False
        )
        self.assertEqual(qs.count(), 3)
    
    def test_num_points(self):
        GeomModel.objects.create(
            ph = Path([(1,2),(2,3),(3,4)])
        )
        GeomModel.objects.create(
            ph = Path([(1,2),(2,3),(3,4),(7,1)])
        )

        qs = GeomModel.objects.filter(ph__numpoints=3)
        self.assertEqual(qs.count(), 4)

        qs = GeomModel.objects.filter(ph__numpoints_gt=3)
        self.assertEqual(qs.count(), 1)

        qs = GeomModel.objects.filter(ph__numpoints_lte=4)
        self.assertEqual(qs.count(), 5)

    def test_center(self):
        qs = GeomModel.objects.filter(
            bx__center=Point([1,1])
        )
        self.assertEqual(qs.count(), 1)
