# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.views.static import serve

app_name = 'tracker'
# the newer version of django should be able to support path() instead
from . import views

urlpatterns = [
    # regular rendering view would be views.index
    url(r'^$', views.IndexView.as_view(), name='index'),
    # (?P<building_pk>[0-9]+) should be able to be replaced by <int:building_pk>
    # DetailView generic view expects the primary key valure captured from the URL to be called "pk"
    url(r'^view/(?P<pk>[0-9]+)/$', views.BuildView.as_view(), name='build_view'),
    # Since this leads to a function, there is no generic view
    url(r'^error/(?P<buildingpk>[0-9]+)/(?P<eventpk>[0-9]+)/$', views.change_error, name='change_error'),
    url(r'^process/(?P<buildingpk>[0-9]+)/(?P<eventpk>[0-9]+)/$', views.process_data, name='process_data'),
    url(r'building/add/$', views.BuildingCreate.as_view(), name='building-add'),
    url(r'building/(?P<pk>[0-9]+)/$', views.BuildingUpdate.as_view(), name='building-update'),
    url(r'event/$', views.EventList.as_view(), name='event-list'),
    url(r'event/(?P<pk>[0-9]+)/$', views.EventView.as_view(), name='event-view'),
    url(r'event/add/$', views.EventCreate.as_view(), name='event-add'),
    url(r'report/add/$', views.ReportCreate.as_view(), name='report-add'),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, { 
            'document_root':settings.MEDIA_ROOT,
            }),
    ]