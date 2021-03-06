# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
import datetime

W = 'Wood'
C = 'Concrete'
RC = 'Reinforced Concrete'
RS = 'Reinforced Steel'
SRC = 'Steel Reinforced Concrete'
S = 'Steel'
BI = 'Base Isolated'
Other = 'Other'
NA = 'Unspecified'

Good = 'Good'
Caut = 'Caution'
Dang = 'Danger'
Abno = 'Abnormal'
Noin = 'Not Enough Info'

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

BUILDING_STATUS = (
    (Good, 'Good'),
    (Caut, 'Caution'),
    (Dang, 'Dangerous'),
    (Abno, 'Abnormal'),
    (Noin, 'Not Enough Info')
)


class Building(models.Model):
    # General Information
    name = models.CharField(max_length=64)
    affiliation = models.CharField(max_length=64, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to="buildings/image")
    floors_above = models.IntegerField(default=1)
    floors_below = models.IntegerField(default=0)
    construction_date = models.DateTimeField(auto_now_add=False, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)
    structure_type = models.CharField(
        max_length=50,
        choices=BUILDING_TYPE,
        default='Unspecified',
    )
    height = models.FloatField(default=0, blank=True)
    width_ns = models.FloatField(default=0, blank=True)
    width_ew = models.FloatField(default=0, blank=True)
    general_info = models.CharField(max_length=512, default='None')
    # Contexual Information
    country = models.CharField(max_length=32, default='None')
    state = models.CharField(max_length=32, default='None')
    city = models.CharField(max_length=32, default='None')
    postal = models.CharField(max_length=16, default='None')
    address1 = models.CharField(max_length=256, default='None')
    address2 = models.CharField(max_length=256, default='None')
    latitude = models.FloatField(default=0, blank=True)
    longitude = models.FloatField(default=0, blank=True)
    cannot_find_address = models.BooleanField(default=False)
    contex_info = models.CharField(max_length=512, default='None', blank=True)
    # Accelerometer Information
    # Perhaps make this a separate class and link the id with Building
    acc_top_floor = models.IntegerField(default=-1)
    acc_top_detail = models.CharField(max_length=512, default='None', blank=True)
    acc_bot_floor = models.IntegerField(default=-1)
    acc_bot_detail = models.CharField(max_length=512, default='None', blank=True)
    sampling_rate = models.FloatField(default=0, blank=True)  # Set Default
    conversion_factor = models.FloatField(default=0, blank=True)  # Set Default
    # Post Process Data
    predominant_periods = ArrayField(models.FloatField(), null=True,
                                     default=[], blank=True)
    predominant_period_avg = models.FloatField(default=-1, blank=True),
    graph_predominant_period = models.ImageField(blank=True, null=True,
                                                 upload_to='buildings/predominant')
    predominant_periods_smooth = ArrayField(models.FloatField(), null=True,
                                            default=[], blank=True)
    graph_predominant_period_smooth = models.ImageField(blank=True, null=True,
                                                        upload_to='buildings/smooth/predominant')
    warning_spots = ArrayField(models.FloatField(), null=True, default=[], blank=True)
    # Status
    warning_message = models.CharField(max_length=512, 
                                       default='Not Enough Data',
                                       blank=True)
    building_status = models.CharField(
        max_length=50,
        choices=BUILDING_STATUS,
        default=Noin
    )
    modified_event = models.IntegerField(default=0, blank=True)
    last_renovation_date = models.DateTimeField(default=datetime.datetime(1950, 1, 16),
                                                blank=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.affiliation)


class Event(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    # General Information
    add_time = models.DateTimeField(auto_now_add=True)
    event_time = models.DateTimeField(auto_now_add=False)
    duration = models.IntegerField(default=0, blank=True)
    intensity = models.FloatField(default=-1, blank=True)
    number = models.IntegerField(default=0, blank=True) #delete this

    # Analitical Information
    acceleration_top = ArrayField(models.FloatField(), default=[], blank=True)
    acceleration_bot = ArrayField(models.FloatField(), default=[], blank=True)
    fourier_top = ArrayField(models.FloatField(), default=[], blank=True)
    fourier_bot = ArrayField(models.FloatField(), default=[], blank=True)
    transfer_function = ArrayField(models.FloatField(), default=[], blank=True)
    predominant_period = models.FloatField(default=0, blank=True, null=True)
    error = models.BooleanField(default=True, blank=True)
    might_be_error = models.BooleanField(default=False, blank=True)
    confirmed_not_error = models.BooleanField(default=False, blank=True)
    geo_not_error = models.BooleanField(default=False, blank=True)
    processed = models.BooleanField(default=False, blank=True)

    # Images and Documnets
    acceleration_top_graph = models.ImageField(blank=True, null=True,
                                               upload_to='event/acceleration/top/graph')
    acceleration_bot_graph = models.ImageField(blank=True, null=True,
                                               upload_to='event/acceleration/bot/graph')
    fourier_top_graph = models.ImageField(blank=True, null=True,
                                          upload_to='event/fourier/top/graph')
    fourier_bot_graph = models.ImageField(blank=True, null=True,
                                          upload_to='event/fourier/bot/graph')
    fourier_top_graph_smooth = models.ImageField(blank=True, null=True,
                                                 upload_to='event/fourier/top/smooth/graph')
    fourier_bot_graph_smooth = models.ImageField(blank=True, null=True,
                                                 upload_to='event/fourier/bot/smooth/graph')                                       
    transfer_function_graph = models.ImageField(blank=True, null=True,
                                                upload_to='event/transfer/graph')
    transfer_function_graph_smooth = models.ImageField(blank=True, null=True,
                                                       upload_to='event/transfer/smooth/graph') 
    acceleration_top_file = models.FileField(blank=True, null=True,
                                             upload_to="event/acceleration/top/data")
    acceleration_bot_file = models.FileField(blank=True, null=True,
                                             upload_to="event/acceleration/bot/data")

    def __str__(self):
        return 'Event ID: {} on {}, Intensity of {}.'.format(self.pk,
                                                             self.event_time,
                                                             self.intensity)
    
    class Meta:
        ordering = ['event_time']


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
    begin_modification = models.DateTimeField(null=True)
    end_modification = models.DateTimeField(null=True)
    add_time = models.DateTimeField(auto_now_add=True)
    occurance = models.CharField(
        max_length=20,
        choices=OCCURANCE,
        default='Other',
    )
    image1 = models.ImageField(blank=True, null=True,
                               upload_to='report')
    image2 = models.ImageField(blank=True, null=True,
                               upload_to='report')
    image3 = models.ImageField(blank=True, null=True,
                               upload_to='report')
    image4 = models.ImageField(blank=True, null=True,
                               upload_to='report')
    comment = models.CharField(max_length=1024)

    def __str__(self):
        return 'Report ID: {} on {}, Building of {}.'.format(self.pk,
                                                             self.add_time,
                                                             self.building.name)
