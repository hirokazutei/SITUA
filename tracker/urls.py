# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url
from . import views
from django.contrib import admin
from django.conf import settings
from django.views.static import serve

app_name = 'tracker'
# the newer version of django should be able to support path() instead

urlpatterns = [
    # regular rendering view would be views.index
    url(r'^$', views.IndexView.as_view(), name='index'),
    # (?P<building_pk>[0-9]+) should be able to be replaced by <int:building_pk>
    # DetailView generic view expects the primary key valure captured from the URL to be called "pk"
    url(r'^view/(?P<pk>[0-9]+)/$', views.BuildView.as_view(), name='build_view'),
    # Since this leads to a function, there is no generic view

    url(r'^buildings', views.BuildList.as_view(), name='build_list'),
    url(r'building/add/$', views.BuildingCreate.as_view(), name='building-add'),
    url(r'^process_building/(?P<buildingpk>[0-9]+)/$', views.process_building, name='process_building'),
    url(r'building/updata/(?P<pk>[0-9]+)/$', views.BuildingUpdate.as_view(), name='building-update'),

    url(r'event/$', views.EventList.as_view(), name='event-list'),
    url(r'^process_event/(?P<buildingpk>[0-9]+)/(?P<eventpk>[0-9]+)/$', views.process_event, name='process_event'),
    url(r'event/(?P<pk>[0-9]+)/$', views.EventView.as_view(), name='event-view'),
    url(r'event/add/$', views.EventCreate.as_view(), name='event-add'),
    url(r'event/edit/(?P<buildingpk>[0-9]+)/(?P<pk>[0-9]+)/$', views.EventUpdate.as_view(), name='event_edit'),
    url(r'^error/(?P<buildingpk>[0-9]+)/(?P<eventpk>[0-9]+)/$', views.change_error, name='change_error'),

    url(r'report/(?P<pk>[0-9]+)/$', views.ReportList.as_view(), name='report-list'),
    url(r'report/view/(?P<pk>[0-9]+)/$', views.ReportView.as_view(), name='report-view'),
    url(r'report/add/$', views.ReportCreate.as_view(), name='report-add'),
    url(r'report/edit/(?P<pk>[0-9]+)/$', views.ReportUpdate.as_view(), name='report-update'),

    # API
    url(r'^API/Upload/$', views.APIupload, name='APIupload'),

    # Confirm Not Error
    url(r'^confirmed_not_error/(?P<buildingpk>[0-9]+)/(?P<eventpk>[0-9]+)/$', views.confirmed_not_error,
        name='confirmed_not_error'),
]

admin.autodiscover()
urlpatterns += [
    url(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
        }),
    url(r'text/(?P<path>.*)$', serve, {
        'document_root': settings.TEXT_ROOT,
        }),
]
