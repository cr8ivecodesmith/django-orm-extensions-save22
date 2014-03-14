# -*- coding: utf-8 -*-

from django.db import models
from django_orm.postgresql.manager import Manager


class TestModel(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField()
    
    objects = models.Manager()
    manager = Manager()


class Person(models.Model):
    name = models.CharField(max_length=32)

    objects = models.Manager()
    manager = Manager()

    def __unicode__(self):
        return self.name
