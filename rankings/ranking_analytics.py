from __future__ import print_function
# -*- coding: utf-8 -*-
__author__ = 'Kambiz'

import sys
sys.path.insert(0, '/home/kaminem64/itunes')
sys.path.insert(0, '/home/kaminem64/itunes/app')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'itunes.settings'
import django
django.setup()

import datetime
from dateutil.rrule import rrule, MONTHLY
import numpy
from app.models import *
from django.db.models import Avg
import collections
import math

# rankings_file = open('exports/rankings.csv', 'w')
# rankings_file.write('store_app_id;category;chart;first_appearance;last_appearance;\
#                     n_observations;n_gaps;mean_gap;std_gap;gaps;mean_rank;std_rank;\
#                     min_rank;max_rank;single_gaps;two_cons_gaps;three_cons_gaps;four_plus_cons_gaps\n')
# rankings_file.close()
categories = AppAnnieRankings.objects.order_by('category').values_list('category', flat=True).distinct()
start_date = datetime.datetime.strptime('2014-01-01', '%Y-%m-%d')
end_date = datetime.datetime.strptime('2016-01-01', '%Y-%m-%d')
for category in categories:
    for rank_type in ['free', 'paid', 'grossing']:
        ranking_analytics = []
        apps = AppAnnieRankings.objects.filter(category=category, rank_type=rank_type).values_list('store_app_id', flat=True).distinct()
        number_of_apps = len(apps)
        current_app = 0
        print('working on', number_of_apps, 'apps from', rank_type, category, 'category...')
        for store_app_id in apps:
            app_data_points = AppAnnieRankings.objects.filter(store_app_id=store_app_id, category=category, rank_type=rank_type).order_by('date')
            n_appearances = app_data_points.count()
            mean_rank = app_data_points.aggregate(Avg('rank'))['rank__avg']
            first_appearance = app_data_points.earliest('date').date
            first_appearance = len([dt for dt in rrule(MONTHLY, dtstart=start_date, until=first_appearance)])

            gaps = []
            n_of_gaps = 0
            last_data_point = 0
            ranks = []
            counter = 0
            for data_point in app_data_points:
                ranks.append(data_point.rank)
                current_date = data_point.date
                if last_data_point:
                    gap = len([dt for dt in rrule(MONTHLY, dtstart=last_data_point, until=current_date)])-2
                    if gap:
                        n_of_gaps += 1
                    gaps.append(gap)
                last_data_point = current_date
            last_appearance = last_data_point
            last_appearance = len([dt for dt in rrule(MONTHLY, dtstart=start_date, until=last_appearance)])
            if not gaps:
                gaps = []
                mean_gap = 0
                std_gap = 0
                one_cons_gap=0
                two_cons_gap=0
                three_cons_gap=0
                four_plus_cons_gap=0
            else:
                mean_gap = numpy.mean(gaps)
                std_gap = numpy.std(gaps)
                # """ Get frequency of consecutive gaps """ # it is wrong because I misunderstood Dr. Jabr's point
                # gap_string = ''.join(str(int(math.ceil(gap*0.00000001))) for gap in gaps)
                # gap_string_split = gap_string.split('0')
                # freq_list = [len(gap) for gap in gap_string_split]
                # freq_dict=dict(collections.Counter(freq_list))

                freq_dict = dict(collections.Counter(gaps))
                try:
                    one_cons_gap = freq_dict[1]
                except:
                    one_cons_gap = 0
                try:
                    two_cons_gap = freq_dict[2]
                except:
                    two_cons_gap = 0
                try:
                    three_cons_gap = freq_dict[3]
                except:
                    three_cons_gap = 0

                four_plus_cons_gap=0
                for i in range(4,15):
                    try:
                        four_plus_cons_gap += freq_dict[i]
                    except:
                        pass
            std_rank = numpy.std(ranks)
            min_rank = min(ranks)
            max_rank = max(ranks)
#             rankings_file = open('exports/rankings.csv', 'a')
#             row = '%d;%s;%s;%d;%d;%d;%d;%f;%f;%s;%f;%f;%d;%d;%d;%d;%d;%d\n' %(store_app_id, category, rank_type, first_appearance, last_appearance,
#                                       n_appearances, n_of_gaps, mean_gap, std_gap, gaps, mean_rank, std_rank, min_rank, max_rank, one_cons_gap,
#                                                                               two_cons_gap, three_cons_gap, four_plus_cons_gap)
#             rankings_file.write(row)
#             """ Maybe later we add app name to the output table """
# rankings_file.close()

            ranking_analytics.append(
                RankingsAnalytics(store_app_id=store_app_id,
                                  category=category,
                                  rank_type=rank_type,
                                  first_appearance=first_appearance,
                                  last_appearance=last_appearance,
                                  n_observations=n_appearances,
                                  n_gaps=n_of_gaps,
                                  mean_gap=mean_gap,
                                  std_gap=std_gap,
                                  gaps=str(gaps),
                                  mean_rank=mean_rank,
                                  std_rank=std_rank,
                                  min_rank=min_rank,
                                  max_rank=max_rank,
                                  single_gaps=one_cons_gap,
                                  two_cons_gaps=two_cons_gap,
                                  three_cons_gaps=three_cons_gap,
                                  four_plus_cons_gaps=four_plus_cons_gap
                                  )
            )
            current_app += 1
            if current_app%100 == 0:
                print(round((current_app*1.0)/number_of_apps, 3)*100, '% completed!')
        RankingsAnalytics.objects.bulk_create(ranking_analytics, batch_size=100000)

