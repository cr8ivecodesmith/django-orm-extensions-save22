# -*- coding: utf-8 -*-

from django.db import models
from django_orm.postgresql.manager import Manager
from django_orm.postgresql.fields.bytea import ByteaField, LargeObjectField

class ByteaModel(models.Model):
     data = ByteaField()
     objects = Manager()

class LargeObjectModel(models.Model):
    lobj = LargeObjectField(default=None, null=True)
    objects = Manager()
