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
from django.db.models import Avg, Count
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta
import datetime

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
    start_date = first_rn.replace(day=1) + relativedelta(months=1)
if start_date < GLOBAL_FIRST_DATE:
    start_date = GLOBAL_FIRST_DATE
last_rn = releasenotes.latest('date').date
if last_rn > GLOBAL_LAST_DATE:
    last_rn = GLOBAL_LAST_DATE

for window in rrule(MONTHLY, dtstart=start_date, until=last_rn):
    try:
        rank = AppAnnieRankings.objects.get(store_app_id=store_app_id, date=window).rank
    except:
        rank = None
    try:
        rank_t_1 = AppAnnieRankings.objects.get(store_app_id=store_app_id, date=window-relativedelta(months=1)).rank
    except:
        rank_t_1 = None
    latest_releasenote_date = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False, date__lte=window).latest('date').date
    # rn_t = ReleaseNote.objects.filter(store_app_id=store_app_id, date__range(datetime.datetime(window.year, window.month-1), datetime.datetime(window.year, window.month)))
    # rn_t_1 = ReleaseNote.objects.filter(store_app_id=store_app_id, date__range(datetime.datetime(window.year, window.month-2), datetime.datetime(window.year, window.month-1)))
    # rn_t_2 = ReleaseNote.objects.filter(store_app_id=store_app_id, date__range(datetime.datetime(window.year, window.month-3), datetime.datetime(window.year, window.month-2)))
    rn_t_1 = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False, date__range=(window-relativedelta(months=1), window))
    rn_t_2 = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False, date__range=(window-relativedelta(months=2), window-relativedelta(months=1)))

    leadusers_feedback = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=True, date__range=(window-relativedelta(months=20), window-relativedelta(months=1))).values('user_apple_id').annotate(Count('id')).order_by().filter(id__count__gt=1)
    for user in leadusers_feedback:
        print(user)

    forward_feedback = ReviewReleaseNoteSim.objects.filter(similarity__gt= 0.2,releasenote__in=rn_t_1, date__range=(window-relativedelta(months=2), window-relativedelta(months=1)))
    # forward_feedback_valance = forward_feedback.aggregate(avg=Avg('star_rating'))
    forward_feedback_volume = forward_feedback.count()
    backward_engagement = ReviewReleaseNoteSim.objects.filter(similarity__gt= 0.2 ,releasenote__in=rn_t_2, date__range=(window-relativedelta(months=1), window))
    backward_engagement_valence = backward_engagement.aggregate(avg=Avg('star_rating'))
    backward_engagement_volume = backward_engagement.count()

    version_cum_volume = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=True, date__range=(latest_releasenote_date, window)).count()
    # total_cum_volume = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=True, date__lte= window).count()
    print(window)
    print('rank:', rank)
    print('rank_t_1:', rank_t_1)
    print(forward_feedback.count())
    print(latest_releasenote_date)
    print(version_cum_volume)
    # print(total_cum_volume)
