from __future__ import print_function
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '/home/kaminem64/itunes')
sys.path.insert(0, '/home/kaminem64/itunes/app')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'itunes.settings'
import django
django.setup()

import numpy as np
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY

from app.models import *


app_id_list = RankingsAnalytics.objects.filter(n_observations__gte=10).order_by('store_app_id').values_list('store_app_id', flat=True).distinct()
apps = App.objects.filter(store_app_id__in=app_id_list)

def release_type_finder(release):
    version = release.version
    dots = version.count('.')
    # print(version, dots)
    if dots > 1:
        return 'minor'
    else:
        return 'major'

def rank_impact_calculator(release):
    """
    1: This function should be changed if we use weekly ranking instead of monthly
    2: We assume rank of app after dropping out of top 500 is 550
    """
    previous_date = release.date.replace(day=1, hour=0, minute=0, second=0)
    next_date = previous_date + relativedelta(months=1)

    try:
        previous_rank = AppAnnieRankings.objects.get(store_app_id=release.app.store_app_id, date=previous_date).rank
    except:
        previous_rank = 550
    try:
        next_rank = AppAnnieRankings.objects.get(store_app_id=release.app.store_app_id, date=next_date).rank
    except:
        next_rank = 550
    rank_impact = previous_rank - next_rank
    return {'previous_rank': previous_rank, 'next_rank':next_rank, 'rank_impact':rank_impact}


# for app in apps:
#     major_release_impact = []
#     minor_release_impact = []
#     for release in AppAnnieReleaseNote.objects.filter(app=app):
#         release_type = release_type_finder(release)
#         rank_impact = rank_impact_calculator(release)
#         print(app.name, rank_impact['previous_rank'], rank_impact['rank_impact'], rank_impact['next_rank'], release_type)
#         # release.previous_rank = rank_impact['previous_rank']
#         # release.rank_impact = rank_impact['rank_impact']
#         # release.release_type = release_type
#         # release.save()
#         """
#         if we draw on all previous data and not only let's say passed 12 periods:
#         """
#         if release_type == 'major':
#             major_release_impact.append(rank_impact['rank_impact'])
#         elif release_type == 'minor':
#             minor_release_impact.append(rank_impact['rank_impact'])
#     if not major_release_impact:
#         major_release_impact = [0]
#     if not minor_release_impact:
#         minor_release_impact = [0]
#     major_release_std = np.std(major_release_impact)
#     major_release_min = np.min(major_release_impact)
#     major_release_max = np.max(major_release_impact)
#     minor_release_std = np.std(minor_release_impact)
#     minor_release_min = np.min(minor_release_impact)
#     minor_release_max = np.max(minor_release_impact)



for app in apps:
    major_release_impact = []
    major_release_base = []
    minor_release_impact = []
    minor_release_base = []
    no_release_impact = []
    no_release_base = []
    first_rank_date = AppAnnieRankings.objects.filter(store_app_id=app.store_app_id).order_by('date')[0].date.replace(day=1, hour=0, minute=0, second=0)
    last_rank_date = AppAnnieRankings.objects.filter(store_app_id=app.store_app_id).order_by('-date')[0].date
    for t1 in rrule(MONTHLY, dtstart=first_rank_date, until=last_rank_date):
        t2 = t1 + relativedelta(months=1)
        try:
            rank1 = AppAnnieRankings.objects.get(store_app_id=app.store_app_id, date=t1).rank
        except:
            rank1 = 550
        try:
            rank2 = AppAnnieRankings.objects.get(store_app_id=app.store_app_id, date=t2).rank
        except:
            rank2 = 550
        delta_rank = rank2 - rank1
        releases = AppAnnieReleaseNote.objects.filter(app=app, date__range=(t1, t2))
        if not releases:
            no_release_impact.append(delta_rank)
            no_release_base.append(rank1)
        else:
            for release in releases:
                release_type = release_type_finder(release)
                print(rank1, delta_rank, rank2, release_type)
                if release_type=='major':
                    major_release_impact.append(delta_rank)
                    major_release_base.append(rank1)
                else:
                    minor_release_impact.append(delta_rank)
                    minor_release_base.append(rank1)
    if not major_release_impact:
        major_release_impact = [0]
    if not minor_release_impact:
        minor_release_impact = [0]
    if not no_release_impact:
        no_release_impact = [0]
    major_release_std = np.std(major_release_impact)
    major_release_min = np.min(major_release_impact)
    major_release_max = np.max(major_release_impact)
    minor_release_std = np.std(minor_release_impact)
    minor_release_min = np.min(minor_release_impact)
    minor_release_max = np.max(minor_release_impact)
    no_release_std = np.std(no_release_impact)
    no_release_min = np.min(no_release_impact)
    no_release_max = np.max(no_release_impact)

    print('app', app.name, 'major_release_std', major_release_std, 'minor_release_std', minor_release_std, 'no_release_std', no_release_std)
    """
    This fundtion should recieve a time at which we are calculating the risk of each decision, and a number of periods which
    is the number of periods we go back to create the lists (e.g. major_release_impact etc.)
    """