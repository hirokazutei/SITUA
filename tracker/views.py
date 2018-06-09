# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.urls import reverse, reverse_lazy
from django.template import loader
import json
from django.views import generic
import dateparser
from cgi import parse_qs, escape
from django.views.decorators.csrf import csrf_exempt
import requests
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView # Create form
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect

from .analysis import AnalyzeEvent, SmoothenPredominantPeriod, AppendPeriod, AveragePeriod, WarningSigns

from .models import Building, Event, Report

from django.contrib.auth import authenticate, login


class IndexView(generic.ListView):
    template_name = 'tracker/index.html'
    context_object = 'building_list'

    def get_queryset(self):
        return Building.objects.all()


class EventList(generic.ListView):
    template_name = 'tracker/event-list.html'
    context_object = 'event_list'

    def get_queryset(self):
        return Event.objects.all()


#Changed from DetailView
class BuildView(generic.DetailView):
    model = Building
    template_name = 'tracker/build_view.html'


class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ['name', 'affiliation', 'image', 'floors_above', 'floors_below',
                  'construction_date', 'general_info', 'address', 'structure_type',
                  'height', 'width_ns', 'width_ew', 'contex_info', 'acc_top_floor',
                  'acc_bot_floor', 'acc_top_detail', 'acc_bot_detail']
        widgets = {
            'construction_date': forms.SelectDateWidget(),
            'general_info': forms.Textarea,
            'contex_info': forms.Textarea
        }


class BuildingCreate(CreateView):
    form_class = BuildingForm
    model = Building
    success_url = reverse_lazy("tracker:index")


class BuildingUpdate(UpdateView):
    form_class = BuildingForm
    model = Building
    success_url = reverse_lazy("tracker:index")


class EventView(generic.DetailView):
    model = Event
    # By default, it will choose template called
    # <app name>/<model name>_detail.html
    # template_name changes that default
    template_name = 'tracker/event_view.html'


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


class EventCreate(CreateView):
    form_class = EventForm
    model = Event
    success_url = reverse_lazy("tracker:index")


class EventUpdate(UpdateView):
    form_class = EventForm
    model = Event
    success_url = reverse_lazy("tracker:index")


class ReportList(generic.DetailView):
    model = Building
    template_name = 'tracker/report-list.html'


class ReportView(generic.DetailView):
    model = Report
    template_name = 'tracker/report-view.html'


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['building', 'begin_modification', 'end_modification', 'occurance', 'comment', 'image1', 'image2', 'image3', 'image4']
        widgets = {
            'end_modification': forms.SelectDateWidget(),
            'begin_modification': forms.SelectDateWidget(),
            'comment': forms.Textarea
        }


class ReportCreate(CreateView):
    form_class = ReportForm
    model = Report
    success_url = reverse_lazy("tracker:index")


class ReportUpdate(UpdateView):
    form_class = ReportForm
    model = Report
    success_url = reverse_lazy("tracker:index")


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


def process_building(request, buildingpk):
    building = get_object_or_404(Building, pk=buildingpk)
    print(SmoothenPredominantPeriod(building))
    return HttpResponseRedirect(reverse('tracker:index'))


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


""" This is the non generic view method to return rendered views

def index(request):
        building_list = get_list_or_404(Building)
        return render(request, 'tracker/index.html',\
         {'building_list': building_list})


def build_view(request, building_pk):
        building = get_object_or_404(Building, pk=building_pk)
        try:
                event = get_list_or_404(Event, building=building_pk)
        except Exception as error:
                return render(request, 'tracker/build_view.html', {
                        'building': building,
                        'error': error})
        return render(request, 'tracker/build_view.html', {
                'building': building,
                'event': event,
                })


def build_edit(request, building_pk):
        building = get_object_or_404(Building, pk=building_pk)
        return render(request, 'tracker/build_edit.html'\
         {'building': building})
        """

"""
#Making Users
class UserFormView(View):
    form_class = UserForm
    template_name = 'upload/registration_form.html'

    def get(self, request):
        form = self.form_class(None) #Use the user form
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False) #does not save in database

            # cleaned (normalized) data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            #email = form.cleaned_data['email']
            #association = form.cleaned_data['association']
            #first_name = form.cleaned_data['first_name']
            #last_name = form.cleaned_data['last_name']
            user.save()

            #returns user objects if credentials are correct
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('upload:index')
        return render(request, self.template_name, {'form': form})
"""
