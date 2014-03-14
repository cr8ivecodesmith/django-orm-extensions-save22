# -*- coding: utf-8 -*-

from django.db import connection
from django.test import TestCase
from django.utils import unittest

from .models import TestModel
from django.core.cache import cache

class OrmCacheTest(TestCase):
    def setUp(self):
        self.ob1 = TestModel.objects.create(name='A')
        self.ob2 = TestModel.objects.create(name='B')
        self.obj3 = TestModel.objects.create(name='C')
        TestModel.objects.create(name='D')
        TestModel.objects.create(name='E')
        TestModel.objects.create(name='F')

    def tararDown(self):
        cache.clear()
        TestModel.objects.all().delete()

    def test_num_querys_object_cache(self):
        with self.assertNumQueries(1):
            TestModel.manager.cache().get(pk=self.ob1.id)
            TestModel.manager.cache().get(pk=self.ob1.id)
    
    def test_num_querys_object_cache_2(self):
        with self.assertNumQueries(1):
            TestModel.manager.cache().get(pk=self.ob1.id)
            TestModel.manager.cache().get(pk=self.ob1.id, name='A')

    def test_num_querys_object_cache_invalidation(self):
        with self.assertNumQueries(2):
            TestModel.manager.cache().get(pk=self.ob1.id)
            obj = TestModel.manager.cache().get(pk=self.ob1.id)
            obj.save()
            TestModel.manager.cache().get(pk=self.ob1.id)

    def test_num_querys_object_cache_3(self):
        with self.assertNumQueries(1):
            TestModel.manager.cache().get(pk=self.ob1.id)
            TestModel.manager.no_cache().get(pk=self.ob1.id)
    
    def test_num_querys_queryset_byid(self):
        with self.assertNumQueries(4):
            list(TestModel.manager.cache().all().byid())
            list(TestModel.manager.cache().all().byid())
            list(TestModel.manager.cache().all().byid())
