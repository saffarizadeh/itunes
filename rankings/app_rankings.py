# -*- coding: utf-8 -*-
__author__ = 'Kambiz'

import sys
sys.path.insert(0, '/home/kambiz/itunes')
sys.path.insert(0, '/home/kambiz/itunes/app')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'itunes.settings'
import django
django.setup()

from app.models import *

import urllib2
import re
import json
import datetime
from lxml import etree


#-------------------------------------------------------------------------------------------#

class AppRanking(object):
    def __init__(self):
        self.user_agent = 'iTunes/12.3.2  (Macintosh; Intel Mac OS X 10.5.8) AppleWebKit/533.16'

    def transfer_initial_rankings(self):
        crawled_apps = ToCrawl.objects.filter(is_crawled=True)
        for crawled_app in crawled_apps:
            print crawled_app.store_app_id
            app = App.objects.get(store_app_id=int(crawled_app.store_app_id))
            Ranking.objects.update_or_create(app=app, date=crawled_app.date, type=crawled_app.rank_type,
                                             defaults={'rank': crawled_app.rank}
                                             )
#
# rank_update = AppRanking()
# rank_update.transfer_initial_rankings()

import csv
def export():

    with open('your.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        # write your header first
        for obj in Ranking.objects.all():
            row = ""

            writer.writerow(row)
export()