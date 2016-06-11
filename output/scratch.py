from __future__ import print_function
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '/home/kaminem64/itunes')
sys.path.insert(0, '/home/kaminem64/itunes/app')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'itunes.settings'
import django
django.setup()

from app.models import *
from django.db.models import Avg
from dateutil.rrule import rrule, MONTHLY
import datetime
from dateutil.relativedelta import relativedelta

GLOBAL_FIRST_DATE = datetime.datetime(2014, 1, 1)
GLOBAL_LAST_DATE = datetime.datetime(2016, 1, 1)

store_app_id=353263352

releasenotes = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False).order_by('id')

# create app-specific time windows
first_rn = releasenotes.earliest('date').date
first_rn = first_rn.replace(hour=0, minute=0, second=0)
if first_rn.day == 1:
    start_date = datetime.datetime(first_rn.year, first_rn.month, 1)
else:
    start_date = first_rn + relativedelta(months=1)
if start_date < GLOBAL_FIRST_DATE:
    start_date = GLOBAL_FIRST_DATE
last_rn = releasenotes.latest('date').date
if last_rn > GLOBAL_LAST_DATE:
    last_rn = GLOBAL_LAST_DATE

for window in rrule(MONTHLY, dtstart=start_date, until=last_rn):
    # if app_in has a ranking: rank else: None
    rank = 100
    # rn_t = ReleaseNote.objects.filter(store_app_id=store_app_id, date__range(datetime.datetime(window.year, window.month-1), datetime.datetime(window.year, window.month)))
    # rn_t_1 = ReleaseNote.objects.filter(store_app_id=store_app_id, date__range(datetime.datetime(window.year, window.month-2), datetime.datetime(window.year, window.month-1)))
    # rn_t_2 = ReleaseNote.objects.filter(store_app_id=store_app_id, date__range(datetime.datetime(window.year, window.month-3), datetime.datetime(window.year, window.month-2)))
    rn_t_1 = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False, date__range=(window-relativedelta(months=1), window))
    rn_t_2 = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False, date__range=(window-relativedelta(months=2), window-relativedelta(months=1)))

    forward_feedback = ReviewReleaseNoteSim.objects.filter(similarity__gt= 0.2,releasenote__in=rn_t_1, date__range=(window-relativedelta(months=2), window-relativedelta(months=1)))
    backward_engagement = ReviewReleaseNoteSim.objects.filter(similarity__gt= 0.2 ,releasenote__in=rn_t_2, date__range=(window-relativedelta(months=1), window))
    average_rating = forward_feedback.aggregate(avg=Avg('star_rating'))
    print(window)
    print(forward_feedback.count())
    print(average_rating)
