# -*- coding: utf-8 -*-
import os
from __future__ import unicode_literals
from django import forms
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
# from django.forms.widgets import SelectDateWidget
from django.urls import reverse, reverse_lazy
# from django.template import loader
import json
from django.views import generic
import dateparser
# from cgi import parse_qs, escape
from django.views.decorators.csrf import csrf_exempt
# import requests
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from .analysis import AnalyzeEvent, SmoothenPredominantPeriod, AppendPeriod, AveragePeriod, WarningSigns
from .models import Building, Event, Report
# google map API
import googlemaps


# Generic view to display list of buildings
class IndexView(generic.ListView):
    template_name = 'tracker/index.html'
    context_object = 'building_list'

    def get_queryset(self):
        return Building.objects.all()


class BuildList(generic.ListView):
    template_name = 'tracker/build_list.html'
    context_object = 'building_list'

    def get_queryset(self):
        return Building.objects.all()


# Generic view to display list of events
class EventList(generic.ListView):
    template_name = 'tracker/event-list.html'
    context_object = 'event_list'

    def get_queryset(self):
        return Event.objects.all()


# Generic Detail view of the building
class BuildView(generic.DetailView):
    model = Building
    template_name = 'tracker/build_view.html'


# The form for filling in building information
class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ['name', 'affiliation', 'image', 'floors_above', 'floors_below',
                  'construction_date', 'general_info', 'country', 'city',
                  'postal', 'address1', 'address2', 'structure_type',
                  'height', 'width_ns', 'width_ew', 'contex_info', 'acc_top_floor',
                  'acc_bot_floor', 'acc_top_detail', 'acc_bot_detail']
        widgets = {
            'construction_date': forms.SelectDateWidget(),
            'general_info': forms.Textarea,
            'contex_info': forms.Textarea
        }


# The view to create a building object
class BuildingCreate(CreateView):
    form_class = BuildingForm
    model = Building
    success_url = reverse_lazy("tracker:index")


# The view to update building object
class BuildingUpdate(UpdateView):
    form_class = BuildingForm
    model = Building
    success_url = reverse_lazy("tracker:index")


# The detailed view of the events
class EventView(generic.DetailView):
    model = Event
    # By default, it will choose template called
    # <app name>/<model name>_detail.html
    # template_name changes that default
    template_name = 'tracker/event_view.html'


# The form for filling in Event Information
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['building', 'duration', 'event_time',
                  'acceleration_top', 'acceleration_bot',
                  'acceleration_bot_file', 'acceleration_top_file']
        widgets = {
            'event_time': forms.SelectDateWidget(),
            'acceleration_top': forms.Textarea,
            'acceleration_bot': forms.Textarea
        }

# The view to create event objects
class EventCreate(CreateView):
    form_class = EventForm
    model = Event
    success_url = reverse_lazy("tracker:index")


# The view to update event objects
class EventUpdate(UpdateView):
    form_class = EventForm
    model = Event
    success_url = reverse_lazy("tracker:index")


# The list view of report objects
class ReportList(generic.ListView):
    model = Building
    template_name = 'tracker/report-list.html'


# The detailed view of report objects
class ReportView(generic.DetailView):
    model = Report
    template_name = 'tracker/report-view.html'


# The form to fill in report information
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['building', 'begin_modification', 'end_modification', 'occurance',
                  'comment', 'image1', 'image2', 'image3', 'image4']
        widgets = {
            'end_modification': forms.SelectDateWidget(),
            'begin_modification': forms.SelectDateWidget(),
            'comment': forms.Textarea
        }


# The form to create a report objects
class ReportCreate(CreateView):
    form_class = ReportForm
    model = Report
    success_url = reverse_lazy("tracker:index")


# The form to update a report objects
class ReportUpdate(UpdateView):
    form_class = ReportForm
    model = Report
    success_url = reverse_lazy("tracker:index")


# The link to process events, using the AnalyzeEvent function
def process_event(request, buildingpk, eventpk):
    building = get_object_or_404(Building, pk=buildingpk)
    try:
        analyze_event = get_object_or_404(Event, pk=eventpk)
    except Exception as error:
        return render(request, 'tracker/build_view.html', {
            'building': building,
            'error_message': error,
        })
    else:
        message, status = AnalyzeEvent(analyze_event, analyze_event.acceleration_top,
                                       analyze_event.acceleration_bot)
        if status != "Error":
            message = "Event {} has been processed!".format(eventpk)
        return render(request, 'tracker/build_view.html', {
            'building': building,
            'message': message,
        })
        # return HttpResponseRedirect(reverse('tracker:build_view',
        #                                    args=(building.pk,)))


# The link to process buildings
def process_building(request, buildingpk):
    building = get_object_or_404(Building, pk=buildingpk)
    print(AppendPeriod(building))
    print(SmoothenPredominantPeriod(building))
    print(AveragePeriod(building))
    print(WarningSigns(building))
    return HttpResponseRedirect(reverse('tracker:index'))


# The link associated with changing the Event
def change_error(request, buildingpk, eventpk):
    building = get_object_or_404(Building, pk=buildingpk)
    try:
        # The value associated with 'Event' is passed in as a POST request,
        # this case, the private key
        error_event = Event.objects.get(pk=eventpk)
    except (KeyError, Event.DoesNotExist):
        return render(request, 'tracker/build_view.html', {
            'building': building,
            'error_message': "Event Does Not Exist!",
        })
    except Exception as error:
        return render(request, 'tracker/build_view.html', {
            'building': building,
            'error_message': error,
        })
    else:
        if error_event.error:
            error_event.error = False
        else:
            error_event.error = True
        error_event.save()
        # Use HttpResponseRedirect for successful POST request as convention
        # Reverse avoid hardcoding urls
        return HttpResponseRedirect(reverse('tracker:build_view',
                                            args=(building.pk,)))


def confirmed_not_error(request, buildingpk, eventpk):
    event = get_object_or_404(Event, pk=eventpk)
    event.confirmed_not_error = True
    event.save()
    return HttpResponseRedirect(reverse('tracker:build_view', args=(buildingpk)))


def buidling_modified(request, buildingpk):
    building = get_object_or_404(Building, pk=buildingpk)
    try:
        events = Event.objects.all().filter(building=building)
        last_event = max(events.id)
        event = Event.objects.all().filter(id=last_event)
        event.confirmed_not_error = True
        building.modified_event = last_event
        building.predominant_periods = []
        building.predominant_period_avg = []
        building.predominant_periods_smooth = []
        building.warning_message = 'Building Predominant Period Permanantly Changed; Currently Not Enough Data'
        building.building_status = 'Not Enough Info'
        building.save()
    except Exception as err:
        return err, "Error"
    return HttpResponseRedirect(reverse('tracker:report-add'))


# The function to handle API uploads
@csrf_exempt
def APIupload(request):
    if request.method == "POST":
        e = json.loads(request.body)
        acc_top = e['acceleration_top']
        acc_bot = e['acceleration_bot']
        try:
            building = get_object_or_404(Building, pk=e['building'])
            if '\n' in acc_top:
                acc_top = acc_top.split('\n')
                acc_bot = acc_bot.split('\n')
            e = Event(building=building,
                      event_time=dateparser.parse(e['event_time']),
                      acceleration_top=e['acceleration_top'],
                      acceleration_bot=e['acceleration_bot'])
            e.save()
            try:
                msg, status = AnalyzeEvent(e, e.acceleration_top, e.acceleration_bot)
                if status == "Error":
                    return HttpResponse(msg)
            except Exception:
                return HttpResponse('Analyze Event Failed')
            try:
                msg, status = AppendPeriod(building)
                if status == "Error":
                    return HttpResponse(msg)
            except Exception:
                return HttpResponse("AppendPeriod Failed")
            try:
                msg, status = SmoothenPredominantPeriod(building)
                if status == "Error":
                    return HttpResponse(msg)
            except Exception as err:
                return HttpResponse("Smoothen Predominant Period Failed")
            # Average Period
            try:
                msg, status = AveragePeriod(building)
                if status == "Error":
                    return HttpResponse(msg)
            except Exception:
                return HttpResponse("Average Period Failed")
            try:
                msg, status = WarningSigns(building)
                if status == "Error":
                    return HttpResponse(msg)
            except Exception:
                return HttpResponse("Warning Signs Failed")
            try:
                    print(building.predominant_period_avg)
                    if int(building.predominant_period_avg) > 0:
                        percent_change = int(building.predominant_period_avg / e.predominant_period)
                        if percent_change > 1.3:
                            e.might_be_error = True
                        elif percent_change > 1.6:
                            e.might_be_error = True
                        elif percent_change < 0.8:
                            e.might_be_error = True
                        elif percent_change < 0.6:
                            e.might_be_error = True
            except Exception as err:
                print(err)
                return HttpResponse('Warnings Failed')
        except Exception as err:
            return HttpResponseBadRequest
    print(building.predominant_period_avg)
    return HttpResponse('<h1>Event Added and Processed</h1>')


def find_address(request, buildingpk):
    building = get_object_or_404(Building, pk=buildingpk)
    google_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if google_key:
        print("Set the 'GOOGLE_MAP_API_KEY' on your environment varaible")
    try:
        gm = googlemaps.Client(key=google_key)
        result = gm.geocode('{}, {}, {}, {}, {}, {}'.format(building.postal,
                                                            building.country,
                                                            building.state,
                                                            building,city,
                                                            building.address1,
                                                            building.address2))
        building.latitude = result[0]['geometry']['location']['lat']
        building.longitude = result[0]['geometry']['location']['lng'])
        building.save()
    except Exception as err:
        building.cannot_find_address == True
        print(err)
    return HttpResponseRedirect(reverse('tracker:build_view', args=(buildingpk)))