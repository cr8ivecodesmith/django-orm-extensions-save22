# -*- coding: utf-8 -*-

from django.db import models
from django_orm.postgresql.fields.arrays import ArrayField
from django_orm.postgresql.manager import Manager

class IntModel(models.Model):
     lista = ArrayField(dbtype='int')
     objects = Manager()
 
class TextModel(models.Model):
    lista = ArrayField(dbtype='text')
    objects = Manager()

class DoubleModel(models.Model):
    lista = ArrayField(dbtype='double precision')
    objects = Manager()

