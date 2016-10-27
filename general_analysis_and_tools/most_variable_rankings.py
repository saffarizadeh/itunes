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
import xlsxwriter
from dateutil.relativedelta import relativedelta

row_num = 0

workbook = xlsxwriter.Workbook('app_rankins.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write(row_num, 0, 'store_app_id')
worksheet.write(row_num, 1, 'app_name')
worksheet.write(row_num, 2, 'category')
worksheet.write(row_num, 3, 'rank_type')
worksheet.write(row_num, 4, 'date')
worksheet.write(row_num, 5, 'period')
worksheet.write(row_num, 6, 'rank')
worksheet.write(row_num, 7, 'number_releases_before_to_this_rank')

apps = []
for rank_type in ['free', 'paid', 'grossing']:
    apps.extend(RankingsAnalytics.objects.filter(n_gaps=0, rank_type=rank_type, n_observations__gte=20, std_rank__gte=120))
app_list=[]


for app in apps:
    try:
        app_list.append(App.objects.get(store_app_id=app.store_app_id))
    except:
        pass
app_list = list(set(app_list))

for app in app_list:
    for rank_type in ['free', 'paid', 'grossing']:
        rankings = AppAnnieRankings.objects.filter(rank_type=rank_type, store_app_id=app.store_app_id)
        period = 0
        for ranking in rankings:
            number_releases = AppAnnieReleaseNote.objects.filter(app=app, date__range=((ranking.date-relativedelta(months=1)), ranking.date) ).count()
            row_num += 1
            worksheet.write(row_num, 0, app.store_app_id)
            worksheet.write(row_num, 1, app.name)
            worksheet.write(row_num, 2, app.category.name)
            worksheet.write(row_num, 3, ranking.rank_type)
            worksheet.write(row_num, 4, ranking.date.strftime('%Y/%m/%d'))
            worksheet.write(row_num, 5, period)
            worksheet.write(row_num, 6, ranking.rank)
            worksheet.write(row_num, 7, number_releases)
            period += 1

workbook.close()


