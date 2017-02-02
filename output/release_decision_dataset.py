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
from dateutil.rrule import rrule, MONTHLY, DAILY
from dateutil.relativedelta import relativedelta
import datetime
import pickle
import pandas as pd

MINIMUM_NUMBER_OF_RANKINGS = 10
MINIMUM_NUMBER_OF_RELEASES = 2
start_date = datetime.date(2016, 10, 1)
end_date = datetime.date(2017, 1, 1)

apps = App.objects.filter(is_releasenotes_crawled=True).order_by('id')
"""
for now we just use the app main category as is define NOW and rank_type as is defined by the price NOW.
we also only use either free or paid (not grossing). later we can add grossing to have simingly unreated equations
"""
for app in apps:
    store_app_id = app.store_app_id
    """ we have to map categories later"""
    category = app.category.name.lower()
    rank_type = 'free' if app.price == 0 else 'paid'
    # print(store_app_id, category, rank_type)

    all_releases = AppAnnieReleaseNote.objects.filter(store_app_id=store_app_id).order_by('-id')
    all_releases_count = AppAnnieReleaseNote.objects.filter(store_app_id=store_app_id,
                                                            date__range=(start_date, end_date)).count()

    all_rankings = AppAnnieRankings.objects.filter(store_app_id=store_app_id,
                                                   category=category,
                                                   rank_type=rank_type,
                                                   )
    all_rankings_count = AppAnnieRankings.objects.filter(store_app_id=store_app_id,
                                                   category=category,
                                                   rank_type=rank_type,
                                                   date__range = (start_date, end_date),
                                                   ).count()
    # print(all_releases_count, all_rankings_count)
    if (all_releases_count >= MINIMUM_NUMBER_OF_RELEASES and all_rankings_count >= MINIMUM_NUMBER_OF_RANKINGS):
        # start_date = all_releases[0].date
        # end_date = all_releases.order_by('id')[0].date

        df_all_releases = pd.DataFrame(list(all_releases.values()))
        df_all_rankings = pd.DataFrame(list(all_rankings.values()))
        index = pd.date_range(start=start_date, end=end_date, freq='D')
        WINDOW = relativedelta(days=1)
        columns = ['store_app_id', 'rank', 'note', 'version']
        data = pd.DataFrame(index=index, columns=columns)
        data = data.fillna(0)
        data['store_app_id'] = store_app_id
        # print(df_all_rankings)
        # data.loc[data['store_app_id'] == df_all_rankings['store_app_id'], 'rank'] = df_all_rankings['rank']
        # print(data)

        # for window in rrule(DAILY, dtstart=start_date, until=end_date):
        for window, row in data.iterrows():
            start = window.to_datetime().strftime('%Y-%m-%d')
            end = window.to_datetime() + WINDOW
            end = end.strftime('%Y-%m-%d')

            ranks = df_all_rankings[(df_all_rankings.date >= start) & (df_all_rankings.date < end)]
            if not ranks.empty:
                """ if we have more than one ranking in the window, we use the average rank """
                data.loc[window, 'rank'] = ranks['rank'].mean()
            releases = df_all_releases[(df_all_releases.date >= start) & (df_all_releases.date < end)]
            if not releases.empty:
                """ if we have more than one release note we join them by 5 new lines """
                data.loc[window, 'note'] = '\n\n\n\n\n'.join(list(releases['note'].values))
                data.loc[window, 'version'] = '\n\n\n\n\n'.join(list(releases['version'].values))


        data.to_csv('%s.csv'%(store_app_id), sep='\t', encoding='utf-8')
