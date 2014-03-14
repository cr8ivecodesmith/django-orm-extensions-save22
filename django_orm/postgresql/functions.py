# -*- coding: utf-8 -*-

from django.db import models
from django_orm.core.sql import SqlFunction

""" 
Functions for varchar and text fields. 
"""

class Unaccent(SqlFunction):
    sql_function = 'unaccent'

class BitLength(SqlFunction):
    sql_function = "bit_length"

