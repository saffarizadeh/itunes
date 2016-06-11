from __future__ import print_function
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


for app in App.objects.filter(store_app_id__in=[320029256, 353263352]): #(is_reviews_crawled=True):
    for releasenote in ReleaseNote.objects.filter(app=app):
        ReviewReleaseNoteFlat.objects.create(store_app_id=app.store_app_id,
                                     is_review=False,
                                     version=releasenote.version,
                                     body=releasenote.note,
                                     date=releasenote.date,
                                     crawled_on=releasenote.crawled_on)
    for review in ReviewFlat.objects.filter(store_app_id=app.store_app_id):
        if review.title and review.body:
            body = review.title + ' . ' + review.body
        elif not review.title and review.body:
            body = review.body
            print('No Title', review.id)
        elif review.title and not review.body:
            body = review.title
            print('No Body', review.id)
        else:
            body = ''
            print('Nothing!', review.id)
        ReviewReleaseNoteFlat.objects.create(store_app_id=app.store_app_id,
                                     is_review=True,
                                     review_id=review.review_id,
                                     body=body,
                                     star_rating=review.star_rating,
                                     username=review.username,
                                     user_apple_id=review.user_apple_id,
                                     user_reviews_url=review.user_reviews_url,
                                     date=review.date,
                                     crawled_on=review.crawled_on)
