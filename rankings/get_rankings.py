# -*- coding: utf-8 -*-
__author__ = 'Kambiz'

import sys
sys.path.insert(0, '/home/kambiz/itunes')
sys.path.insert(0, '/home/kambiz/itunes/app')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'itunes.settings'
import django
django.setup()

import re
import datetime
from dateutil.relativedelta import relativedelta
import lxml.html
from app.models import *

def get_ranking(html_source, date, category):
    html = lxml.html.fromstring(html_source)

    ranking_obj = []

    for i, rank_type in [(2,'free'), (3, 'paid'), (4, 'grossing')]:
        app_names=[]
        app_urls = []
        seller_names = []
        seller_ids = []
        store_app_ids=[]
        ranks = range(1, len(html.xpath("//tr/td[%d]//*[contains(@class, 'app-name')]/span"%i))+1 )

        for app_name in html.xpath("//tr/td[%d]//*[contains(@class, 'app-name')]/span"%i):
            try:
                app_names.append(app_name.text[:150])
            except:
                app_names.append(0)
        """ We can use these urls to get the missing app_ids later (if needed)"""
        for app_url in html.xpath("//tr/td[%d]//*[contains(@class, 'app-name')]"%i):
            try:
                app_urls.append(app_url.attrib['href'])
            except:
                app_urls.append(0)
        for img in html.xpath('//tr/td[%d]/div/div/a/img'%i):
            store_app_id = img.attrib['src']
            try:
                store_app_id = re.search('ios/(.+)/', store_app_id).group(1)
                store_app_ids.append(store_app_id)
            except:
                store_app_ids.append(0)

        for seller_name in html.xpath("//tr/td[%d]//*[contains(@class, 'publisher-name')]/span"%i):
            try:
                seller_names.append(seller_name.text[:150])
            except:
                seller_names.append(0)
        for seller in html.xpath("//tr/td[%d]//*[contains(@class, 'publisher-name')]"%i):
            seller_id = seller.attrib['href']
            try:
                seller_id = re.search('(company|publisher)/(.+)/', seller_id).group(2)
                seller_ids.append(seller_id)
            except:
                seller_ids.append(0)

        for rank, store_app_id, app_name, seller_id, seller_name, app_url in zip(ranks, store_app_ids, app_names, seller_ids, seller_names, app_urls):
            ranking_obj.append(
                                AppAnnieRankings(store_app_id=store_app_id,
                                app_name=app_name[:200],
                                rank_type=rank_type,
                                category=category[:200],
                                seller_id=seller_id,
                                seller_name=seller_name[:200],
                                app_url=app_url,
                                rank=rank,
                                date=date)
                               )
    AppAnnieRankings.objects.bulk_create(ranking_obj, batch_size=10000)


from selenium import webdriver
from time import sleep

print('Launching Chromium..')
# browser = webdriver.Firefox()
browser = webdriver.Chrome('./chromedriver')
print('Entering AppAnnie')
browser.get('https://www.appannie.com/account/login/')

username = browser.find_element_by_id("email")
password = browser.find_element_by_id("password")
username.send_keys("kaminem64@yahoo.com")
password.send_keys("linux116")
browser.find_element_by_id("submit").click()

# categories = ['books','business','catalogs','education','entertainment','finance','food-and-drink',
#               'games','health-and-fitness','lifestyle','newsstand', 'medical','music','navigation','news','photo-and-video',
#               'productivity','reference','shopping','social-networking','sports','travel','utilities','weather']

categories = ['finance','navigation','social-networking']


#------------ add 2013 (at least 4 more months
# dates = ['2013-11-01', '2013-12-01', '2014-01-01', '2014-02-01', '2014-03-01', '2014-04-01', '2014-05-01', '2014-06-01',
#          '2014-07-01', '2014-08-01', '2014-09-01', '2014-10-01', '2014-11-01', '2014-12-01', '2015-01-01', '2015-02-01',
#          '2015-03-01', '2015-04-01', '2015-05-01', '2015-06-01', '2015-07-01', '2015-08-01', '2015-09-01', '2015-10-01',
#          '2015-11-01', '2015-12-01', '2016-01-01']

dates = []
date = datetime.date(2016, 10, 1)
while date != datetime.date(2017, 1, 1):
    dates.append(date)
    date += relativedelta(days=1)

for category in categories:
    for date in dates:
        url = 'https://www.appannie.com/apps/ios/top-chart/united-states/'+category+'/?page_size=500&device=iphone&date='+date.strftime("%Y-%m-%d")
        browser.get(url)
        # try:
        #     browser.find_element_by_class_name("load-all").click()
        # except:
        #     try:
        #         re.search('''There is no ranking data available on this date, for the selected country and category.''', browser.page_source).group()
        #         continue
        #     except:
        #         input("Press Enter to continue...")
        #         # url = 'https://www.appannie.com/apps/ios/top-chart/united-states/'+category+'/?device=iphone&date='+date
        #         browser.get(url)
        #         browser.find_element_by_class_name("load-all").click()
        sleep(3)
        html_source = browser.page_source
        # date = datetime.datetime.strptime(date, '%Y-%m-%d')
        get_ranking(html_source=html_source, date=date, category=category)

browser.close()
