# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.template import loader
from django.views import generic
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView #Create form
from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect

from .analysis import AnalyzeEvent

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
    # By default, it will choose template called
    # <app name>/<model name>_detail.html
    # template_name changes that default
    template_name = 'tracker/build_view.html'


class BuildingCreate(CreateView):
    model = Building
    fields = ['name', 'affiliation', 'image', 'floors_above', 'floors_below',
              'construction_date', 'general_info', 'address', 'structure_type',
              'height', 'width_ns', 'width_ew', 'contex_info', 'acc_top_floor',
              'acc_bot_floor', 'acc_top_detail', 'acc_bot_detail']
    success_url = reverse_lazy("tracker:index")


class BuildingUpdate(UpdateView):
    model = Building
    fields = ['name', 'affiliation', 'image' 'floors_above', 'floors_below',
              'construction_date', 'general_info', 'address', 'structure_type',
              'height', 'width_ns', 'width_ew', 'contex_info', 'acc_top_floor',
              'acc_bot_floor', 'acc_top_detail', 'acc_bot_detail']
    success_url = reverse_lazy("tracker:index")
    #might not need success here


class EventView(generic.DetailView):
    model = Event
    # By default, it will choose template called
    # <app name>/<model name>_detail.html
    # template_name changes that default
    template_name = 'tracker/event_view.html'


class EventCreate(CreateView):
    model = Event
    fields = ['building', 'duration', 'event_time',
              'acceleration_top', 'acceleration_bot',
              'acceleration_bot_file', 'acceleration_top_file']
    success_url = reverse_lazy("tracker:index")


class EventUpdate(UpdateView):
    model = Event
    fields = ['building', 'duration', 'event_time',
              'acceleration_top', 'acceleration_bot',
              'acceleration_bot_file', 'acceleration_top_file']
    success_url = reverse_lazy("tracker:index")


class ReportView(generic.DetailView):
    model = Report
    template_name = 'tracker/report-view.html'


class ReportCreate(CreateView):
    model = Report
    fields = ['building', 'occurance', 'comment']
    success_url = reverse_lazy("tracker:index")


def process_data(request, buildingpk, eventpk):
    building = get_object_or_404(Building, pk=buildingpk)
    try:
        analyze_event = get_object_or_404(Event, pk=eventpk)
    except Exception as error:
        return render(request, 'tracker/build_view.html', {
            'building': building,
            'error_message': error,
        })
    else:
        message, status = AnalyzeEvent(analyze_event, analyze_event.acceleration_top, analyze_event.acceleration_bot)
        if status != "Error":
            message = "Event {} has been processed!".format(eventpk)
        return render(request, 'tracker/build_view.html', {
            'building': building,
            'message': message,
        })
        #return HttpResponseRedirect(reverse('tracker:build_view',
        #                                    args=(building.pk,)))


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
