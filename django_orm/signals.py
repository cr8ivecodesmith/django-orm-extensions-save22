# -*- coding: utf-8 -*-

import django.dispatch
pre_syncdb = django.dispatch.Signal(providing_args=[])
