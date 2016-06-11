# -*- coding: utf-8 -*-
__author__ = 'Kambiz'

import sys
sys.path.insert(0, '/home/kaminem64/itunes')
sys.path.insert(0, '/home/kaminem64/itunes/app')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'itunes.settings'
import django
django.setup()

from app.models import *
from django.utils.encoding import smart_str
import xlsxwriter
workbook = xlsxwriter.Workbook('app_list_1.xlsx')
worksheet = workbook.add_worksheet()

NA_apps = []

row_num = 0
worksheet.write(row_num, 0, 'store_app_id')
worksheet.write(row_num, 1, 'appfigures_id')
worksheet.write(row_num, 2, 'name')
worksheet.write(row_num, 3, 'url')
worksheet.write(row_num, 4, 'description')
worksheet.write(row_num, 5, 'seller')
worksheet.write(row_num, 6, 'category')
worksheet.write(row_num, 7, 'size')
worksheet.write(row_num, 8, 'current_version')
worksheet.write(row_num, 9, 'first_release_date')
worksheet.write(row_num, 10, 'price')
worksheet.write(row_num, 11, 'minimum_os_version')
worksheet.write(row_num, 12, 'user_rating_count')
worksheet.write(row_num, 13, 'average_user_rating')
worksheet.write(row_num, 14, 'bundle_id')
worksheet.write(row_num, 15, 'total_pages')
worksheet.write(row_num, 16, 'total_reviews')
worksheet.write(row_num, 17, 'crawled_on')

app_id_list = open('app_list_1.csv', 'r').read().split('\n')
for store_app_id in app_id_list:
    try:
        app = App.objects.get(store_app_id=store_app_id)
        row_num += 1
        worksheet.write(row_num, 0, app.store_app_id)
        worksheet.write(row_num, 1, app.appfigures_id)
        worksheet.write(row_num, 2, app.name)
        worksheet.write(row_num, 3, app.url)
        worksheet.write(row_num, 4, app.description)
        worksheet.write(row_num, 5, app.seller.id)
        worksheet.write(row_num, 6, app.category.id)
        worksheet.write(row_num, 7, app.size)
        worksheet.write(row_num, 8, app.current_version)
        worksheet.write(row_num, 9, app.first_release_date)
        worksheet.write(row_num, 10, app.price)
        worksheet.write(row_num, 11, app.minimum_os_version)
        worksheet.write(row_num, 12, app.user_rating_count)
        worksheet.write(row_num, 13, app.average_user_rating)
        worksheet.write(row_num, 14, app.bundle_id)
        worksheet.write(row_num, 15, app.total_pages)
        worksheet.write(row_num, 16, app.total_reviews)
        worksheet.write(row_num, 17, app.crawled_on)
    except:
        NA_apps.append(store_app_id)
workbook.close()

NA_apps_file=open('NA_apps_1.txt', 'w')
NA_apps_file.write(str(NA_apps))
NA_apps_file.close()