# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

W = 'Wood'
C = 'Concrete'
RC = 'Reinforced Concrete'
RS = 'Reinforced Steel'
SRC = 'Steel Reinforced Concrete'
S = 'Steel'
BI = 'Base Isolated'
Other = 'Other'
NA = 'Unspecified'

BUILDING_TYPE = (
    (W, 'Wood'),
    (C, 'Concrete'),
    (RC, 'Reinforced Concrete'),
    (RS, 'Reinforced Steel'),
    (SRC, 'Steel Reinforced Concrete'),
    (S, 'Steel'),
    (BI, 'Base Isolated'),
    (Other, 'Other'),
    (NA, 'Unspecified')
)

class Building(models.Model):
    # General Information
    name = models.CharField(max_length=64)
    affiliation = models.CharField(max_length=64, blank=True)
    floors_above = models.IntegerField(default=1)
    floors_below = models.IntegerField(default=0)
    construction_date = models.DateTimeField(auto_now_add=False, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)
    general_info = models.CharField(max_length=512, default='None')
    # Contexual Information
    address = models.CharField(max_length=256, default='None')
    latitude = models.FloatField(default=0, blank=True)
    longitude = models.FloatField(default=0, blank=True)
    cannot_find_address = models.BooleanField(default=False)
    structure_type = models.CharField(
        max_length=20,
        choices=BUILDING_TYPE,
        default='Unspecified',
    )
    height = models.FloatField(default=0, blank=True)
    width_ns = models.FloatField(default=0, blank=True)
    width_ew = models.FloatField(default=0, blank=True)
    contex_info = models.CharField(max_length=512, default='None', blank=True)
    # Accelerometer Information
    # Perhaps make this a separate class and link the id with Building
    acc_top_floor = models.IntegerField(default=-1)
    acc_top_detail = models.CharField(max_length=512, default='None', blank=True)
    acc_bot_floor = models.IntegerField(default=-1)
    acc_bot_detail = models.CharField(max_length=512, default='None', blank=True)
    sampling_rate = models.FloatField(default=0, blank=True)  # Set Default
    conversion_factor = models.FloatField(default=0, blank=True)  # Set Default

    def __str__(self):
        return '{} - {}'.format(self.name, self.affiliation)


class Event(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    # General Information
    add_time = models.DateTimeField(auto_now_add=True)
    event_time = models.DateTimeField(auto_now_add=False, blank=True)
    duration = models.IntegerField(default=0, blank=True)
    intensity = models.FloatField(default=-1, blank=True)
    number = models.IntegerField(default=0, blank=True)
    acceleration_top = ArrayField(models.FloatField(), default=[])
    acceleration_bot = ArrayField(models.FloatField(), default=[])
    fourier_top = ArrayField(models.FloatField(), default=[], blank=True)
    fourier_bot = ArrayField(models.FloatField(), default=[], blank=True)
    transfer_function = ArrayField(models.FloatField(), default=[], blank=True)
    predominant_frequency = models.FloatField(default=-1, blank=True)
    error = models.BooleanField(default=False)

    def __str__(self):
        return 'Event ID: {} on {}, Intensity of {}.'.format(self.pk,
                                                             self.event_time,
                                                             self.intensity)


# Report Section
C = 'Construction'
R = 'Renovation'
D = 'Damage'

OCCURANCE = (
    (C, 'Construction'),
    (R, 'Renovation'),
    (D, 'Damage'),
    (Other, 'Other'),
)


class Report(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    # General Information
    begin_modification = models.DateTimeField(auto_now_add=True, blank=True)
    end_modification = models.DateTimeField(auto_now_add=True, blank=True)
    add_time = models.DateTimeField(auto_now_add=True)
    occurance = models.CharField(
        max_length=20,
        choices=OCCURANCE,
        default='Other',
    )
    comment = models.CharField(max_length=1024)

    def __str__(self):
        return 'Report ID: {} on {}, Building of {}.'.format(self.pk,
                                                             self.add_time,
                                                             self.building.name)
                                                             