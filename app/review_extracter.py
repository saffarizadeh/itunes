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
import xml.etree.ElementTree as ET
import os
import re
import datetime
from lxml import etree
from pymongo import MongoClient


class ReviewExtracter(object):
    def __init__(self, app_id):
        self.app_id = app_id
        self.app = App.objects.get(store_app_id=app_id)
        self.xml_folder = 'xml/' + str(self.app_id) + '/'
        self.all_reviews = []

    def extract_review(self, page):
        # page = page.read()
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(page, parser=parser)

        # parser = ET.XMLParser(encoding="utf-8")
        # root = ET.fromstring(page, parser=parser)
        # root = ET.fromstring(page)
        reviews=[]
        stars=[]
        titles=[]
        timestamps=[]
        usernames = []
        user_reviews_url = []
        user_apple_ids = []
        review_ids = []

        #Get Review IDs
        for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}LoadFrameURL'):
            review_ids.append(int(re.search('viewVote(\d+)', node.attrib['frameViewName']).group(1)))
        review_ids = list(set(review_ids))

        #Get Titles
        for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}b'):
            titles.append(node.text)

        #Get Reviews
        for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle'):
            reviews.append(node.text)

        #Get star ratings
        for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}HBoxView'):
            try:
                alt = node.attrib['alt']
                st = int(alt.strip(' stars'))
            except KeyError:
                continue
            stars.append(st)

        #Get Timestamps
        for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}GotoURL/{http://www.apple.com/itms/}b/..'):
            date = re.search('\w\w\w \d\d, \d+', node.tail).group()
            timestamps.append(datetime.datetime.strptime(date, '%b %d, %Y'))

        #Get Usernames
        for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}GotoURL/{http://www.apple.com/itms/}b'):
            usernames.append(node.text.strip())

        #Get User IDs
        for node in root.findall('{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}ScrollView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}View/{http://www.apple.com/itms/}MatrixView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}VBoxView/{http://www.apple.com/itms/}HBoxView/{http://www.apple.com/itms/}TextView/{http://www.apple.com/itms/}SetFontStyle/{http://www.apple.com/itms/}GotoURL'):
            user_reviews_url.append(node.attrib['url'])
            try:
                user_apple_ids.append(int(re.search('userProfileId=(\d+)', node.attrib['url']).group(1)))
            except:
                user_apple_ids.append(int(re.search('dsid=(\d+)', node.attrib['url']).group(1)))

        initial_result = zip(review_ids, titles, reviews, stars, timestamps, usernames, user_reviews_url, user_apple_ids)
        result = []
        for item in initial_result:
            result.append({'review_id': item[0],
                             'title': item[1],
                             'body': item[2],
                             'star_rating': item[3],
                             'date': item[4],
                             'username': item[5],
                             'user_reviews_url': item[6],
                             'user_apple_id': item[7]
                             })
        return result

    def get_all_reviews(self):
        self.all_reviews = []
        client = MongoClient()
        db = client.test
        cursor = db.itunes.find({'store_app_id':self.app_id})
        for document in cursor:
            self.all_reviews.extend(self.extract_review(page=document['page']))
        # for subdir, dirs, files in os.walk(self.xml_folder):
        #     for file_name in files:
        #         page = open(self.xml_folder + file_name, 'r')
        #         self.all_reviews.extend(self.extract_review(page=page))

    def create_user(self, username, user_apple_id, user_reviews_url):
        if User.objects.filter(user_apple_id=user_apple_id).exists():
            user = User.objects.get(user_apple_id=user_apple_id)
        else:
            user = User.objects.create(username=username,
                                       user_apple_id=user_apple_id,
                                       user_reviews_url=user_reviews_url)

        return user

    def create_review(self, user, review_id, title, body, star_rating, date):
        app = App.objects.get(store_app_id=self.app_id)
        if Review.objects.filter(review_id=review_id).exists():
            review = Review.objects.get(review_id=review_id)
        else:
            review = Review.objects.create(app=app,
                                            user=user,
                                            review_id=review_id,
                                            title=title,
                                            body=body,
                                            star_rating=star_rating,
                                            date=date)
        return review

    def save_reviews(self):
        self.get_all_reviews()
        user_objs=[]
        review_objs=[]
        from collections import defaultdict
        id_to_scores = defaultdict(list)
        for review in self.all_reviews:
            id_to_scores[review['user_apple_id']].append(review) #removes duplicate 'user_apple_id's
        for review in id_to_scores.values():
            review = review[0]
            if not User.objects.filter(user_apple_id=review['user_apple_id']).exists():
                user_objs.append(
                                User(username=review['username'],
                                     user_apple_id=review['user_apple_id'],
                                     user_reviews_url=review['user_reviews_url']
                                     )
                                )
        User.objects.bulk_create(user_objs, batch_size=3000)
            # user = self.create_user(username=review['username'],
            #                         user_apple_id=review['user_apple_id'],
            #                         user_reviews_url=review['user_reviews_url'])
            # self.create_review(user=user,
            #                    review_id=review['review_id'],
            #                    title=review['title'],
            #                    body=review['body'],
            #                    star_rating=review['star_rating'],
            #                    date=review['date'])
        for review in self.all_reviews:
            # if not Review.objects.filter(review_id=review['review_id']).count(): #deal with duplicates later
            user = User.objects.get(user_apple_id=review['user_apple_id'])
            review_objs.append(
                        Review(app=self.app,
                                user=user,
                                review_id=review['review_id'],
                                title=review['title'],
                                body=review['body'],
                                star_rating=review['star_rating'],
                                date=review['date'])
                        )
        Review.objects.bulk_create(review_objs, batch_size=1000)


    def flat_save_reviews(self):
        self.get_all_reviews()
        review_objs=[]
        for review in self.all_reviews:
            review_objs.append(
                        ReviewFlat(store_app_id=self.app.store_app_id,
                                   review_id=review['review_id'],
                                   title=review['title'],
                                   body=review['body'],
                                   star_rating=review['star_rating'],
                                   date=review['date'],
                                   username=review['username'],
                                   user_apple_id=review['user_apple_id'],
                                   user_reviews_url=review['user_reviews_url']
                                   )
                        )
        ReviewFlat.objects.bulk_create(review_objs, batch_size=1000)

