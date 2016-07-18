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
import lxml.html
from lxml import etree
from app.models import *
import random

def get_releasenote(html_source):
    html = lxml.html.fromstring(html_source)
    versions_dates = html.xpath("//*[contains(@class, 'app-version-block')]//h5")
    releasenotes = []
    for version_date in versions_dates:
        try:
            date = datetime.datetime.strptime(re.search('\((.+?)\)', version_date.text).group(1), '%b %d, %Y')
            version = re.search(r'Version (.+?) \(', version_date.text).group(1)
            try:
                note = version_date.getnext()
                note = re.sub("[\r\n]+", ".", etree.tostring(note, pretty_print=True))
                note = re.sub("<br />", ".", note)
                note = re.sub("<br/>", ".", note)
                note = '. '.join(re.findall(r'<p>(.+?)</p>', note))
            except:
                note = ''
            releasenotes.append({'date': date, 'version': version, 'note': note})
        except:
            pass
    # notes = html.xpath("//*[contains(@class, 'app-version-note')]")

    return releasenotes


def create_releasenotes(app, releasenotes):
    for releasenote in releasenotes:
        AppAnnieReleaseNote.objects.create(app=app,
                                           date=releasenote['date'],
                                           version=releasenote['version'],
                                           note=releasenote['note'])



from selenium import webdriver
from time import sleep

print 'Launching Chromium..'
# browser = webdriver.Firefox()
browser = webdriver.Chrome('./../rankings/chromedriver')
print 'Entering AppAnnie'
browser.get('https://www.appannie.com/account/login/')

username = browser.find_element_by_id("email")
password = browser.find_element_by_id("password")
username.send_keys("kaminem64@yahoo.com")
password.send_keys("linux116")
browser.find_element_by_id("submit").click()

apps = App.objects.filter(is_reviews_crawled=True, is_releasenotes_crawled=False).order_by('id')

for app in apps:
    app_id = app.store_app_id
    print(app_id)
    save = True
    url = 'https://www.appannie.com/apps/ios/app/'+str(app_id)+'/details/'
    browser.get(url)
    try:
        re.search('''The data was collected from the App Store on''', browser.page_source).group()
    except:
        try:
            re.search('''This application has been removed from the store''', browser.page_source).group()
            print('This application has been removed from the store!!!')
            save = False
        except:
            try:
                re.search('''This asset has been temporarily disabled due to a copyright issue''', browser.page_source).group()
                print('This asset has been temporarily disabled due to a copyright issue!!!')
                save = False
            except:
                raw_input("Press Enter to continue...")
                browser.get(url)
    html_source = browser.page_source
    releasenotes = get_releasenote(html_source=html_source)
    create_releasenotes(app=app, releasenotes=releasenotes)
    if save:
        app.is_releasenotes_crawled=True
        app.save()

    sleep(random.random()*2)

browser.close()
