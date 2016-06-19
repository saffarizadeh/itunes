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

GLOBAL_FIRST_DATE = datetime.datetime(2013, 1, 1)
GLOBAL_LAST_DATE = datetime.datetime(2016, 1, 1)

# store_app_id=353263352
app_ids = ReviewReleaseNoteFlat.objects.all().order_by('store_app_id').values_list('store_app_id',flat=True).distinct()[:100]

for store_app_id in app_ids:
    app = App.objects.get(store_app_id=store_app_id)
    category = app.category.name
    if app.price == 0:
        rank_type = 'free'
    else:
        rank_type = 'paid'
    first_appearance_on_charts = AppAnnieRankings.objects.filter(store_app_id=store_app_id, category=category, rank_type=rank_type).order_by('date').earliest('date').date
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

    leadusers_dict = {}
    leadusers = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=True).values('user_apple_id').annotate(Count('id')).order_by().filter(id__count__gt=1)
    for user in leadusers:
        leadusers_dict[user['user_apple_id']] = 2

    new_leadusers_cumu = 0
    panel_data = []
    for window in rrule(MONTHLY, dtstart=start_date, until=last_rn):
        try:
            rank = AppAnnieRankings.objects.get(store_app_id=store_app_id, date=window).rank
        except:
            rank = None #come up with an algorithm to impude it
        try:
            rank_t_1 = AppAnnieRankings.objects.get(store_app_id=store_app_id, date=window-relativedelta(months=1)).rank
        except:
            rank_t_1 = None
        latest_releasenote_date = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False, date__lte=window).latest('date').date
        # rn_t = ReleaseNote.objects.filter(store_app_id=store_app_id, date__range(datetime.datetime(window.year, window.month-1), datetime.datetime(window.year, window.month)))
        # rn_t_1 = ReleaseNote.objects.filter(store_app_id=store_app_id, date__range(datetime.datetime(window.year, window.month-2), datetime.datetime(window.year, window.month-1)))
        # rn_t_2 = ReleaseNote.objects.filter(store_app_id=store_app_id, date__range(datetime.datetime(window.year, window.month-3), datetime.datetime(window.year, window.month-2)))
        rn_t = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False, date__range=(window-relativedelta(months=1), window))
        rn_t_1 = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False, date__range=(window-relativedelta(months=2), window-relativedelta(months=1)))
        rn_t_2 = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False, date__range=(window-relativedelta(months=3), window-relativedelta(months=2)))

        forward_feedback = ReviewReleaseNoteSim.objects.filter(similarity__gt= 0.2,releasenote__in=rn_t, date__range=(window-relativedelta(months=3), window-relativedelta(months=1)))
        # in this way we will consider this period twice: once here and once in the window that t_1 is t
        # forward_feedback_t_1 = ReviewReleaseNoteSim.objects.filter(similarity__gt= 0.2,releasenote__in=rn_t_1, date__range=(window-relativedelta(months=3), window-relativedelta(months=2)))
        # forward_feedback_valance = forward_feedback.aggregate(avg=Avg('star_rating'))
        forward_feedback_volume = forward_feedback.count()
        backward_engagement_pos = ReviewReleaseNoteSim.objects.filter(star_rating__gt=3, similarity__gt= 0.2 ,releasenote__in=rn_t_2, date__range=(window-relativedelta(months=2), window)).count() # two periods
        backward_engagement_neg = ReviewReleaseNoteSim.objects.filter(star_rating__lte=3, similarity__gt= 0.2 ,releasenote__in=rn_t_2, date__range=(window-relativedelta(months=2), window)).count() # two periods
        # backward_engagement_valence = backward_engagement.aggregate(avg=Avg('star_rating'))
        # backward_engagement_volume = backward_engagement.count() #two separate volumes pos and neg

        period_new_leadusers = 0
        for leaduser in leadusers_dict.keys():
            if ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=True, user_apple_id=leaduser, date__range=(window-relativedelta(months=1), window)).exists():
                leadusers_dict[leaduser] -= 1 #the first appearance doesn't count as being leaduser
            if leadusers_dict[leaduser] == 0:
                period_new_leadusers += 1
                del(leadusers_dict[leaduser])
        new_leadusers_cumu += period_new_leadusers

        version_cumu_volume = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=True, date__range=(latest_releasenote_date, window)).count()
        total_cumu_volume = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=True, date__lte= window).count()
        #----- Control variables: volume up until each release

        try:
            rank_improvement = rank_t_1 - rank
        except:
            rank_improvement = None


        age = window - app.first_release_date


        print(store_app_id)
        print(category)
        print(age.days)
        print(rank_type)
        print(new_leadusers_cumu)
        print(window)
        print(rank_improvement)
        print(forward_feedback_volume)
        print(backward_engagement_pos)
        print(backward_engagement_neg)
        print(version_cumu_volume)
        print(total_cumu_volume)
        print(rank, '\n-----------------------------')
        panel_data.append(
                            PanelData(store_app_id=store_app_id,
                                      category=category,
                                      age=age.days,
                                      type=rank_type,
                                      new_leadusers_cumu=new_leadusers_cumu,
                                      window=window,
                                      rank_improvement=rank_improvement,
                                      forward_feedback_volume=forward_feedback_volume,
                                      backward_engagement_pos=backward_engagement_pos,
                                      backward_engagement_neg=backward_engagement_neg,
                                      version_cumu_volume=version_cumu_volume,
                                      total_cumu_volume=total_cumu_volume,
                                      rank=rank
                                      )
        )
    PanelData.objects.bulk_create(panel_data, batch_size=100000)