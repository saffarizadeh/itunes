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

import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import gensim

store_app_id = 353263352

releasenotes = ReviewReleaseNoteFlat.objects.filter(store_app_id__in=[353263352], is_review=False).order_by('id')
reviews = ReviewReleaseNoteFlat.objects.filter(store_app_id__in=[353263352], is_review=True).order_by('id')

num_topics = 100
tfidf = pickle.load( open( "exports/tfidf.p", "rb" ) )
corpus_gensim = pickle.load( open( "exports/corpus_gensim.p", "rb" ) )
gensim_tfidf = list(corpus_gensim)

lsi_model = gensim.models.LsiModel.load('exports/lsi.model')
lsi_releasenotes_vecs = np.zeros((1,num_topics))
lsi_reviews_vecs = np.zeros((1,num_topics))

count = 0
for doc in releasenotes:
    lsi_releasenotes_vecs = np.vstack((lsi_releasenotes_vecs, gensim.matutils.corpus2dense(lsi_model[[gensim_tfidf[doc.id - 3717281]]], num_topics).T))
    count += 1
lsi_releasenotes_vecs = np.delete(lsi_releasenotes_vecs,0,0)

count = 0
for doc in reviews:
    lsi_reviews_vecs = np.vstack((lsi_reviews_vecs, gensim.matutils.corpus2dense(lsi_model[[gensim_tfidf[doc.id - 3717281]]], num_topics).T))
    count += 1

lsi_reviews_vecs = np.delete(lsi_reviews_vecs,0,0)

lsi_similarity_cosine = cosine_similarity(lsi_reviews_vecs, lsi_releasenotes_vecs)


for releasenote in releasenotes:
   for review in reviews:
       ReviewReleaseNoteSim.objects.create(store_app_id=store_app_id,
                                           releasenote=releasenote,
                                           review=review,
                                           star_rating=review.star_rating,
                                           user_apple_id=review.user_apple_id,
                                           version=releasenote.version,
                                           date=review.date
                                           )
