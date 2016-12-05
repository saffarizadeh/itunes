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


number_of_apps = App.objects.filter(total_reviews__lt=10082.5).count()
number_of_apps_with_rn = AppAnnieReleaseNote.objects.all().order_by('app_id').values_list('app_id', flat=True).distinct().count()
number_of_releasenotes = AppAnnieReleaseNote.objects.all().count()
average_app_number_of_rns = (number_of_releasenotes*1.0)/number_of_apps_with_rn
average_app_rating = App.objects.aggregate(Avg('average_user_rating'))
average_app_rating_count = App.objects.aggregate(Avg('user_rating_count'))
average_app_price = App.objects.aggregate(Avg('price'))
average_paid_app_price = App.objects.filter(price__gt=0).aggregate(Avg('price'))
average_app_size = App.objects.aggregate(Avg('size'))

max_number_of_observations = RankingsAnalytics.objects.all().order_by('-n_observations')[0].n_observations
average_months_on_top500 = RankingsAnalytics.objects.all().aggregate(Avg('n_observations'))



print("number_of_apps: ", number_of_apps)
print("average_app_rating: ", average_app_rating)
print("average_app_rating_count: ", average_app_rating_count)
print("average_app_price: ", average_app_price)
print("average_paid_app_price: ", average_paid_app_price)
print("average_app_size: ", average_app_size)
print("average_app_number_of_rns: ", average_app_number_of_rns)
print("average_months_on_top500: ", average_months_on_top500)
