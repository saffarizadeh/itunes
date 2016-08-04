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
import numpy as np
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


for app in App.objects.filter(is_reviews_crawled=True, is_releasenotes_crawled=True):
    print(app.store_app_id)
    """ Removing Release Notes Duplicate Sentences (we keep first appearance of a sentence) """
    new_rns = []
    vectorizer = TfidfVectorizer(min_df=1, lowercase=True)
    rn_sents = []
    index={}
    for i, releasenote in enumerate(AppAnnieReleaseNote.objects.filter(app=app).order_by('date')[1:]):
        sents = sent_tokenize(releasenote.note.replace('\n','.'))
        index[i] = [j for j in range(len(rn_sents), len(rn_sents)+len(sents))]
        rn_sents.extend(sents)
    rn_sentscopy = rn_sents[:]
    try:
        rn_vectors = vectorizer.fit_transform(rn_sents)
        rn_similarity = cosine_similarity(rn_vectors,rn_vectors)
        np.fill_diagonal(rn_similarity, 0)
        for i in range(rn_similarity.shape[0]):
            for j in range(i, rn_similarity.shape[1]):
                if rn_similarity[i][j]>0.8:
                    if rn_sents[j] == rn_sentscopy[j]:
                        rn_sents[j]=''
        where = np.where(rn_similarity>0.8)
        similar_rn_rn = list(set(where[0]))
        similar_rn_rn_counter = {n:1 for n in similar_rn_rn}

        for sent_index in index.values():
            final_rn = []
            for sent in sent_index:
                if sent in similar_rn_rn:
                    if similar_rn_rn_counter[sent] == 1: # we don't remove the first appearance of a duplicate
                        similar_rn_rn_counter[sent] = 0
                        final_rn.append(rn_sents[sent])
                else:
                    final_rn.append(rn_sents[sent])
            new_rns.append(' '.join(final_rn).strip())
    except Exception as e:
        print(e)
        new_rns.append('')

    reviewsreleasenotes = []
    for i, releasenote in enumerate(AppAnnieReleaseNote.objects.filter(app=app).order_by('date')[1:]):
        reviewsreleasenotes.append(ReviewReleaseNoteFlat(store_app_id=app.store_app_id,
                                                         is_review=False,
                                                         version=releasenote.version,
                                                         body=new_rns[i],
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
