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
import pickle


GLOBAL_FIRST_DATE = datetime.datetime(2013, 11, 1)
GLOBAL_LAST_DATE = datetime.datetime(2016, 1, 1)

tfidf_db_map = pickle.load( open( "../similarity/exports/tfidf_db_map.p", "rb" ) )
print('getting doc ids...')
doc_ids = tfidf_db_map.keys()
print(len(doc_ids))
app_ids = ReviewReleaseNoteFlat.objects.filter(id__in=doc_ids, date__range=(GLOBAL_FIRST_DATE, GLOBAL_LAST_DATE)).order_by('store_app_id').values_list('store_app_id',flat=True).distinct()
print(len(app_ids))
print('doc ids retrieved!')

# app_ids = App.objects.filter(is_reviews_crawled=True).order_by('id').values_list('store_app_id',flat=True)

for store_app_id in app_ids:
    print(store_app_id)
    app = App.objects.get(store_app_id=store_app_id)

    ''' order_by('-n_observations')[0] returns the category-chart with most observations '''
    try:
        app_rankinganalytics = RankingsAnalytics.objects.filter(store_app_id=store_app_id, rank_type__in=['free', 'paid'], n_observations__gte=5,
                                                             single_gaps__lte=1, two_cons_gaps=0, three_cons_gaps=0,
                                                             four_plus_cons_gaps=0).order_by('-n_observations')[0]
    except:
        app_rankinganalytics = RankingsAnalytics.objects.filter(store_app_id=store_app_id, rank_type='grossing', n_observations__gte=5,
                                                             single_gaps__lte=1, two_cons_gaps=0, three_cons_gaps=0,
                                                             four_plus_cons_gaps=0).order_by('-n_observations')[0]
    rank_type = app_rankinganalytics.rank_type
    category = app_rankinganalytics.category
    print(category)
    # free = AppAnnieRankings.objects.filter(store_app_id=store_app_id, category=category,rank_type='free').count()
    # paid = AppAnnieRankings.objects.filter(store_app_id=store_app_id, category=category,rank_type='paid').count()
    # grossing = AppAnnieRankings.objects.filter(store_app_id=store_app_id, category=category,rank_type='grossing').count()
    # if free >= paid and free >= grossing:
    #     rank_type = 'free'
    # elif paid >= free and paid >= grossing:
    #     rank_type = 'paid'
    # else:
    #     rank_type = 'grossing'

    releasenotes = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False).order_by('id')
    ''' in appannie RNs we should skip the first RN which is the first release data-point.
        We consider this when we are making ReviewReleaseNoteFlat table'''
    if ReviewReleaseNoteSim.objects.filter(store_app_id=store_app_id).count() > 0:
        # create app-specific time windows
        first_rn = releasenotes.earliest('date').date
        first_rn = first_rn.replace(hour=0, minute=0, second=0)
        if first_rn.day != 1:
            first_rn = first_rn.replace(day=1) + relativedelta(months=1)

        first_appearance_on_charts = AppAnnieRankings.objects.filter(store_app_id=store_app_id, category=category, rank_type=rank_type).earliest('date').date
        first_appearance_on_charts = first_appearance_on_charts.replace(hour=0, minute=0, second=0)

        start_date = max(first_rn+relativedelta(months=2), first_appearance_on_charts+relativedelta(months=1), GLOBAL_FIRST_DATE)

        last_appearance_on_charts = AppAnnieRankings.objects.filter(store_app_id=store_app_id, category=category, rank_type=rank_type).latest('date').date
        last_rn = releasenotes.latest('date').date
        end_date = min(last_appearance_on_charts, last_rn, GLOBAL_LAST_DATE)

        leadusers_dict = {}
        leadusers = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=True).values('user_apple_id').annotate(Count('id')).order_by().filter(id__count__gt=1)
        for user in leadusers:
            leadusers_dict[user['user_apple_id']] = 2

        new_leadusers_cumu = 0
        panel_data = []
        rank_t_1 = None
        rank_t_p_1 = 'Not calculated!'
        for window in rrule(MONTHLY, dtstart=start_date, until=end_date):
            date_t_1 = window - relativedelta(months=1)
            date_t_2 = window - relativedelta(months=2)
            date_t_p_1 = window + relativedelta(months=1)
            date_t_p_2 = window + relativedelta(months=2)
            if not rank_t_1:
                try:
                    rank_t_1 = AppAnnieRankings.objects.get(store_app_id=store_app_id, category=category, rank_type=rank_type, date=date_t_1).rank
                except:
                    try:
                        rank_t_2 = AppAnnieRankings.objects.get(store_app_id=store_app_id, category=category, rank_type=rank_type, date=date_t_2).rank
                        rank_t = AppAnnieRankings.objects.get(store_app_id=store_app_id, category=category, rank_type=rank_type, date=window).rank
                        rank_t_1 = (rank_t + rank_t_2)/2 # gives an int number
                    except:
                        rank_t_1 = None

            try:
                rank = AppAnnieRankings.objects.get(store_app_id=store_app_id, category=category, rank_type=rank_type, date=window).rank
            except:
                try:
                    rank_t_p_1 = AppAnnieRankings.objects.get(store_app_id=store_app_id, category=category,
                                                              rank_type=rank_type, date=date_t_p_1).rank
                except:
                    try:
                        rank_t_p_2 = AppAnnieRankings.objects.get(store_app_id=store_app_id, category=category,
                                                                  rank_type=rank_type, date=date_t_p_2).rank
                        rank_t = AppAnnieRankings.objects.get(store_app_id=store_app_id, category=category,
                                                              rank_type=rank_type, date=window).rank
                        rank_t_p_1 = (rank_t + rank_t_p_2) / 2  # gives an int number
                    except:
                        rank_t_p_1 = None
                try:
                    rank = (rank_t_p_1 + rank_t_1)/2 # gives an int number
                except:
                    rank = None

            latest_releasenote_date = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False, date__lte=window).latest('date').date

            rn_t = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False, date__range=(window-relativedelta(months=1), window))
            rn_t_1 = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False, date__range=(window-relativedelta(months=2), window-relativedelta(months=1)))
            rn_t_2 = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=False, date__range=(window-relativedelta(months=3), window-relativedelta(months=2)))

            forward_rn_count =  rn_t.count() + rn_t_1.count()
            if forward_rn_count:
                forward_rn_exists = 1
            else:
                forward_rn_exists = 0

            backward_rn_count =  rn_t_2.count() + rn_t_1.count()
            if backward_rn_count:
                backward_rn_exists = 1
            else:
                backward_rn_exists = 0

            forward_feedback_t = ReviewReleaseNoteSim.objects.filter(store_app_id=store_app_id, similarity__gt= 0.2,releasenote__in=rn_t, date__range=(window-relativedelta(months=3), window-relativedelta(months=1))).count()
            forward_feedback_t_1 = ReviewReleaseNoteSim.objects.filter(store_app_id=store_app_id, similarity__gt= 0.2,releasenote__in=rn_t_1, date__range=(window-relativedelta(months=3), window-relativedelta(months=2))).count()
            forward_feedback_volume = forward_feedback_t + forward_feedback_t_1
            # in this way we will consider this period twice: once here and once in the window that t_1 is t

            """ we can also consider word count """
            backward_engagement_pos_t_2 = ReviewReleaseNoteSim.objects.filter(store_app_id=store_app_id, star_rating__gt=3, similarity__gt= 0.2 ,releasenote__in=rn_t_2, date__range=(window-relativedelta(months=2), window)).count()
            backward_engagement_pos_t_1 = ReviewReleaseNoteSim.objects.filter(store_app_id=store_app_id, star_rating__gt=3, similarity__gt= 0.2 ,releasenote__in=rn_t_1, date__range=(window-relativedelta(months=1), window)).count()
            backward_engagement_neg_t_2 = ReviewReleaseNoteSim.objects.filter(store_app_id=store_app_id, star_rating__lte=3, similarity__gt= 0.2 ,releasenote__in=rn_t_2, date__range=(window-relativedelta(months=2), window)).count()
            backward_engagement_neg_t_1 = ReviewReleaseNoteSim.objects.filter(store_app_id=store_app_id, star_rating__lte=3, similarity__gt= 0.2 ,releasenote__in=rn_t_1, date__range=(window-relativedelta(months=1), window)).count()
            backward_engagement_pos = backward_engagement_pos_t_2 + backward_engagement_pos_t_1
            backward_engagement_neg = backward_engagement_neg_t_2 + backward_engagement_neg_t_1

            period_new_leadusers = 0
            allusers = ReviewReleaseNoteFlat.objects.filter(store_app_id=store_app_id, is_review=True,
                                                 date__range=(window - relativedelta(months=2), window)).order_by('user_apple_id').values_list('user_apple_id', flat=True).distinct()
            for leaduser in leadusers_dict.keys():
                if leaduser in allusers:
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

            panel_data.append(
                                PanelData(store_app_id=store_app_id,
                                          category=category,
                                          age=age.days,
                                          type=rank_type,
                                          leadusers_cumu=new_leadusers_cumu,
                                          window=window,
                                          rank_improvement=rank_improvement,
                                          forward_feedback_volume=forward_feedback_volume,
                                          backward_engagement_pos=backward_engagement_pos,
                                          backward_engagement_neg=backward_engagement_neg,
                                          version_cumu_volume=version_cumu_volume,
                                          total_cumu_volume=total_cumu_volume,
                                          rank=rank,
                                          rank_t_1=rank_t_1,
                                          forward_rn_count=forward_rn_count,
                                          forward_rn_exists=forward_rn_exists,
                                          backward_rn_count=backward_rn_count,
                                          backward_rn_exists=backward_rn_exists,
                                          )
            )
            print(rank_t_1, rank, rank_t_p_1, rank_improvement)
            rank_t_1 = rank
        PanelData.objects.bulk_create(panel_data, batch_size=100000)



    # category_map = {
    # 'Book': 'books',
    # 'Business': 'business',
    # 'Catalogs': 'catalogs',
    # 'Education': 'education',
    # 'Entertainment': 'entertainment',
    # 'Finance': 'finance',
    # 'Food & Drink': 'food-and-drink',
    # 'Games': 'games',
    # 'Health & Fitness': 'health-and-fitness',
    # 'Lifestyle': 'lifestyle',
    # 'Medical': 'medical',
    # 'Music': 'music',
    # 'Navigation': 'navigation',
    # 'News': 'news',
    # 'Newsstand': 'newsstand',
    # 'Photo & Video': 'photo-and-video',
    # 'Productivity': 'productivity',
    # 'Reference': 'reference',
    # 'Shopping': 'shopping',
    # 'Social Networking': 'social-networking',
    # 'Sports': 'sports',
    # 'Travel': 'travel',
    # 'Utilities': 'utilities',
    # 'Weather': 'weather'
    # }
    # category = category_map[category]