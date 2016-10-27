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


dates = AppAnnieRankings.objects.all().order_by('date').values_list('date', flat=True).distinct()
categories = AppAnnieRankings.objects.all().order_by('category').values_list('category', flat=True).distinct()

for category in categories:
    for rank_type in ['free','paid']:
        print(category, rank_type)
        for date in dates:
            apps_free_or_paid = list(AppAnnieRankings.objects.filter(date=date, rank_type=rank_type, category=category).order_by('-store_app_id').values_list('store_app_id', flat=True).distinct())
            apps_grossing = list(AppAnnieRankings.objects.filter(date=date, rank_type='grossing', category=category).order_by('-store_app_id').values_list('store_app_id', flat=True).distinct())
            apps_free_or_paid_grossing_intersect = len(apps_free_or_paid) + len(apps_grossing) - len(set(apps_free_or_paid+apps_grossing))
            print(apps_free_or_paid_grossing_intersect)
