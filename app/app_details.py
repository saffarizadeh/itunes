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

import urllib2
import re
import json
import datetime
from lxml import etree


#-------------------------------------------------------------------------------------------#

class AppCrawler(object):
    def __init__(self, app_id, app_store):
        self.app_id = app_id
        self.app_store = app_store
        self.front = '143441'
        self.user_agent = 'iTunes/12.3.2  (Macintosh; Intel Mac OS X 10.5.8) AppleWebKit/533.16'

    def get_total_pages(self):
        page_number = 0
        url = "https://itunes.apple.com/WebObjects/MZStore.woa/wa/viewContentsUserReviews?id=%s&pageNumber=%d&sortOrdering=4&onlyLatestVersion=false&type=Purple+Software" % (self.app_id, page_number)
        req = urllib2.Request(url, headers={"X-Apple-Store-Front": self.front,"User-Agent": self.user_agent})
        u = urllib2.urlopen(req)
        page = u.read()
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(page, parser=parser)
        for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}b'):
            try:
                self.total_pages = re.search('Page 1 of (\d+)', node.text).group(1)
            except:
                self.total_pages = 1
        return int(self.total_pages)

    def create_category(self, category_id, category_name, category_url):
        try:
            category = Category.objects.get(store_category_id=category_id)
        except:
            category = Category.objects.create(store_category_id=category_id,
                                               name=category_name,
                                               url=category_url)
        return category

    def create_seller(self, seller_id, seller_name, seller_url):
        try:
            seller = Seller.objects.get(store_seller_id=seller_id)
        except:
            seller = Seller.objects.create(store_seller_id=seller_id,
                                           name=seller_name,
                                           url=seller_url)
        return seller

    def create_app(self, app_id, app_name, app_url, app_description, seller, category, app_size, app_current_version,
                   app_first_release_date, app_price, app_minimum_os_version, app_user_rating_count,
                   app_average_user_rating, app_bundle_id, total_pages, total_reviews):
        try:
            app = App.objects.get(store_app_id=app_id)
        except:
            app = App.objects.create(store_app_id=app_id,
                                     name=app_name,
                                     url=app_url,
                                     description=app_description,
                                     seller=seller,
                                     category=category,
                                     size=app_size,
                                     current_version=app_current_version,
                                     first_release_date=app_first_release_date,
                                     price=app_price,
                                     minimum_os_version=app_minimum_os_version,
                                     user_rating_count=app_user_rating_count,
                                     average_user_rating=app_average_user_rating,
                                     bundle_id=app_bundle_id,
                                     total_pages=total_pages,
                                     total_reviews=total_reviews)
        return app

    def extract_release_notes(self, page):
        print page
        text = re.search('"versionHistory":(.+)', page).group(1).replace('null','""').replace('true','""')
        print "\n\n\n\n\n\n\n\n\n\n"
        print text
        text = text[text.find('[{'): text.find('}]')+2]
        releases = eval(text)
        release_notes=[]
        for release in releases:
            release_date = datetime.datetime.strptime(release['releaseDate'], '%Y-%m-%dT%H:%M:%SZ')
            # release_note = release['releaseNotes'].decode('raw_unicode_escape') #alleviate bullet point render problem
            release_note = release['releaseNotes']
            release_version = release['versionString']
            release_notes.append({'version': release_version, 'date': release_date, 'note': release_note})
        return release_notes

    def extract_app_details(self, json_result):
        #App
        app_name = json_result['trackCensoredName']
        app_url = "https://itunes.apple.com/%s/app/id%d?mt=8" %(self.app_store, self.app_id)
        app_description = json_result['description']
        app_size = json_result['fileSizeBytes']
        app_current_version = json_result['version']
        app_first_release_date = datetime.datetime.strptime(json_result['releaseDate'], '%Y-%m-%dT%H:%M:%SZ')
        app_price = json_result['price']
        app_minimum_os_version = json_result['minimumOsVersion']
        try:
            app_user_rating_count = json_result['userRatingCount']
        except:
            app_user_rating_count = 0
        try:
            app_average_user_rating = json_result['averageUserRating']
        except:
            app_average_user_rating = 0
        #Seller
        seller_id = json_result['artistId']
        seller_name = json_result['artistName']
        seller_url = 'https://itunes.apple.com/us/developer/id%d' %(seller_id)
        #Category
        category_id = json_result['primaryGenreId']
        category_name = json_result['primaryGenreName']
        category_url = 'https://itunes.apple.com/genre/id%d' %(category_id)
        try:
            app_bundle_id = json_result['bundleId']
        except:
            app_bundle_id = None
        return {'app_id':self.app_id,
                'app_name':app_name,
                'app_url':app_url,
                'app_description':app_description,
                'app_size':app_size,
                'app_current_version':app_current_version,
                'app_first_release_date':app_first_release_date,
                'app_price':app_price,
                'app_minimum_os_version':app_minimum_os_version,
                'app_user_rating_count':app_user_rating_count,
                'app_average_user_rating':app_average_user_rating,
                'seller_id':seller_id,
                'seller_name':seller_name,
                'seller_url':seller_url,
                'category_id':category_id,
                'category_name':category_name,
                'category_url':category_url,
                'app_bundle_id':app_bundle_id}

    def itunes_api_lookup(self):
        result = False
        url = 'https://itunes.apple.com/lookup?id=%d'%(self.app_id)
        req = urllib2.Request(url, headers={"User-Agent": self.user_agent})
        u = urllib2.urlopen(req, timeout=30)
        page = json.load(u)
        try:
            result = page['results'][0]
        except:
            print 'No result for: %d' %(self.app_id)
        return result

    def itunes_app_details_crawl(self):
        app_url = "https://itunes.apple.com/%s/app/id%d?mt=8" %(self.app_store, self.app_id)
        req = urllib2.Request(app_url, headers={"User-Agent": self.user_agent})
        u = urllib2.urlopen(req, timeout=30)
        page = u.read()
        return page

    def create_release_notes(self, release_notes):
        app = App.objects.get(store_app_id=self.app_id)
        for release_note in release_notes:
            try:
                ReleaseNote.objects.get(app=app,
                                        version=release_note['version'])
                pass
            except:
                ReleaseNote.objects.create(app=app,
                                           version=release_note['version'],
                                           date=release_note['date'],
                                           note=release_note['note'])
        return 0

    def get_app(self):
        # App
        json_result = self.itunes_api_lookup()
        if not json_result:
            return False
        app_detail = self.extract_app_details(json_result=json_result)

        category = self.create_category(category_id=app_detail['category_id'],
                                        category_name=app_detail['category_name'],
                                        category_url=app_detail['category_url'])

        seller = self.create_seller(seller_id=app_detail['seller_id'],
                                    seller_name=app_detail['seller_name'],
                                    seller_url=app_detail['seller_url'])

        total_pages = self.get_total_pages()
        total_reviews = total_pages * 25
        self.create_app(app_id=app_detail['app_id'],
                        app_name=app_detail['app_name'][:200],
                        app_url=app_detail['app_url'],
                        app_description=app_detail['app_description'],
                        seller=seller,
                        category=category,
                        app_size=app_detail['app_size'],
                        app_current_version=app_detail['app_current_version'],
                        app_first_release_date=app_detail['app_first_release_date'],
                        app_price=app_detail['app_price'],
                        app_minimum_os_version=app_detail['app_minimum_os_version'],
                        app_user_rating_count=app_detail['app_user_rating_count'],
                        app_average_user_rating=app_detail['app_average_user_rating'],
                        app_bundle_id=app_detail['app_bundle_id'],
                        total_pages=total_pages,
                        total_reviews=total_reviews)

        # Release Notes
        app_details_page = self.itunes_app_details_crawl()
        release_notes = self.extract_release_notes(page=app_details_page)
        self.create_release_notes(release_notes=release_notes)
        return True



# app_details_crawler = AppCrawler(app_id=582654048, app_store='us')
# app_details_page = app_details_crawler.itunes_app_details_crawl()
# release_notes = app_details_crawler.extract_release_notes(page=app_details_page)
# app_details_crawler.create_release_notes(release_notes=release_notes)