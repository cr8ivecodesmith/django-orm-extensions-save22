# -*- coding: utf-8 -*-

from django.db import models

from django_orm.postgresql.manager import Manager
from django_orm.postgresql.geometric.fields import GeometricField
from django_orm.postgresql.geometric.objects import Point, Circle, Box

class SomeObject(models.Model):
    pos = GeometricField(dbtype=Point)
    objects = Manager()

class CircleObjectModel(models.Model):
    carea = GeometricField(dbtype=Circle)
    objects = Manager()

class BoxObjectModel(models.Model):
    barea = GeometricField(dbtype=Box)
    other = models.ForeignKey("CircleObjectModel", related_name="boxes", 
        null=True, default=None)

    objects = Manager()
