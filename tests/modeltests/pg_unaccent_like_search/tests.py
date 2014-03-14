# -*- coding: utf-8 -*-

from django.test import TestCase
from django_orm.postgresql.functions import Unaccent
from django_orm.core.sql import SqlExpression

from .models import TestModel
from .models import Person

class TestUnaccent(TestCase):
    def setUp(self):
        self.p1 = Person.objects.create(name='Andréi')
        self.p2 = Person.objects.create(name='Pèpâ')

    def tearDown(self):
        self.p1.delete()
        self.p2.delete()
    
    def test_annotate(self):
        qs = Person.manager.annotate_functions(
            name_unaccent = Unaccent("name")
        )
        qs = list(qs)
        self.assertEqual(qs[0].name_unaccent, 'Andrei')
        self.assertEqual(qs[1].name_unaccent, 'Pepa')

    def test_statement(self):
        qs = Person.manager.where(
            SqlExpression(Unaccent("name"), "=", "Andrei")
        )
        self.assertEqual(qs.count(), 1)
