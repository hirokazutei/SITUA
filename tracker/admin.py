# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Building, Event, Report

admin.site.register(Building)
admin.site.register(Event)
admin.site.register(Report)
