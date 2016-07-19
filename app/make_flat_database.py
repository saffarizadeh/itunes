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

for app in App.objects.filter(is_reviews_crawled=True, is_releasenotes_crawled=True):
    reviewsreleasenotes = []
    for releasenote in AppAnnieReleaseNote.objects.filter(app=app).order_by('date')[1:]:#.order_by('date')[1:]
        reviewsreleasenotes.append(ReviewReleaseNoteFlat(store_app_id=app.store_app_id,
                                                         is_review=False,
                                                         version=releasenote.version,
                                                         body=releasenote.note,
                                                         date=releasenote.date,
                                                         crawled_on=releasenote.crawled_on)
                                   )
    for review in ReviewFlat.objects.filter(store_app_id=app.store_app_id).order_by('date'):
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
        reviewsreleasenotes.append(ReviewReleaseNoteFlat(store_app_id=app.store_app_id,
                                                        is_review=True,
                                                        review_id=review.review_id,
                                                        body=body,
                                                        star_rating=review.star_rating,
                                                        username=review.username,
                                                        user_apple_id=review.user_apple_id,
                                                        user_reviews_url=review.user_reviews_url,
                                                        date=review.date,
                                                        crawled_on=review.crawled_on)
                                   )
    ReviewReleaseNoteFlat.objects.bulk_create(reviewsreleasenotes, batch_size=100000)
