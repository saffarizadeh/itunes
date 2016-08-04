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
from sklearn.metrics.pairwise import cosine_similarity
import re
import gensim
import pickle
from string import punctuation
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from gensim import matutils
import datetime

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

tokenizer = TweetTokenizer()
punc = re.compile('[%s]' % re.escape(punctuation))
only_english_letters = re.compile(r'[^a-zA-Z ]')

def tokenize_stemmer(text):
    if text:
        text = only_english_letters.sub('', text)
        if text:
            return [stemmer.stem(token) for token in tokenizer.tokenize(gensim.utils.to_unicode(text))]
        else:
            return []
    else:
        return []

GLOBAL_FIRST_DATE = datetime.datetime(2013, 11, 1)
GLOBAL_LAST_DATE = datetime.datetime(2016, 1, 1)

app_ids = ReviewReleaseNoteFlat.objects.all().order_by('store_app_id').values_list('store_app_id',flat=True).distinct()
# app_ids = App.objects.filter(is_reviews_crawled=True).order_by('id').values_list('store_app_id',flat=True)
tfidf_db_map = pickle.load( open( "exports/tfidf_db_map.p", "rb" ) )
print('getting doc ids...')
doc_ids = tfidf_db_map.keys()
print(len(doc_ids))
app_ids = ReviewReleaseNoteFlat.objects.filter(id__in=doc_ids, date__range=(GLOBAL_FIRST_DATE, GLOBAL_LAST_DATE)).order_by('store_app_id').values_list('store_app_id',flat=True).distinct()
print(len(app_ids))
print('doc ids retrieved!')

num_topics = 300
tfidf = pickle.load( open( "exports/tfidf.p", "rb" ) )
# vectorizer = pickle.load( open( "exports/vectorizer.p", "rb" ) )

corpus_gensim = pickle.load( open( "exports/corpus_gensim.p", "rb" ) )
gensim_tfidf = list(corpus_gensim)
lsi_model = gensim.models.LsiModel.load('exports/lsi.model')

print(len(tfidf_db_map.keys()))
print(tfidf.shape)
print(len(gensim_tfidf))

for app_id in app_ids:
    print(app_id)
    releasenotes = ReviewReleaseNoteFlat.objects.filter(store_app_id=app_id, is_review=False, date__range=(GLOBAL_FIRST_DATE, GLOBAL_LAST_DATE)).order_by('id')
    reviews = ReviewReleaseNoteFlat.objects.filter(store_app_id=app_id, is_review=True, date__range=(GLOBAL_FIRST_DATE, GLOBAL_LAST_DATE)).order_by('id')
    # lsi_releasenotes_vecs = np.zeros((1, num_topics))
    # lsi_reviews_vecs = np.zeros((1, num_topics))
    # count = 0
    # for doc in releasenotes:
    #     index = tfidf_db_map[doc.id]
    #     lsi_releasenotes_vecs = np.vstack((lsi_releasenotes_vecs, gensim.matutils.corpus2dense(lsi_model[[gensim_tfidf[index]]], num_topics).T))
    #     count += 1
    # lsi_releasenotes_vecs = np.delete(lsi_releasenotes_vecs,0,0)
    #
    # count = 0
    # for doc in reviews:
    #     index = tfidf_db_map[doc.id]
    #     lsi_reviews_vecs = np.vstack((lsi_reviews_vecs, gensim.matutils.corpus2dense(lsi_model[[gensim_tfidf[index]]], num_topics).T))
    #     count += 1
    #
    # lsi_reviews_vecs = np.delete(lsi_reviews_vecs,0,0)

    """ more memory intensive but faster """
    first_releasenote_index = tfidf_db_map[releasenotes[0].id]
    last_releasenote_index = tfidf_db_map[releasenotes.order_by('-id')[0].id]
    lsi_releasenotes_vecs = gensim.matutils.corpus2dense(lsi_model[gensim_tfidf[first_releasenote_index:last_releasenote_index+1]], num_topics)

    first_review_index = tfidf_db_map[reviews[0].id]
    last_review_index = tfidf_db_map[reviews.order_by('-id')[0].id]
    lsi_reviews_vecs = gensim.matutils.corpus2dense(lsi_model[gensim_tfidf[first_review_index:last_review_index+1]], num_topics)
    lsi_similarity_cosine = cosine_similarity(lsi_reviews_vecs.T, lsi_releasenotes_vecs.T)

    print(releasenotes.count()+reviews.count())
    print('rn', releasenotes.count(), lsi_releasenotes_vecs.shape)
    print('rv', reviews.count(), lsi_reviews_vecs.shape)
    print(lsi_similarity_cosine.shape)

    reviewrelease_objs = []
    for j, releasenote in enumerate(releasenotes):
       for i, review in enumerate(reviews):
           reviewrelease_objs.append(
                           ReviewReleaseNoteSim(store_app_id=app_id,
                                                releasenote=releasenote,
                                                review=review,
                                                star_rating=review.star_rating,
                                                user_apple_id=review.user_apple_id,
                                                version=releasenote.version,
                                                date=review.date,
                                                word_count=len(review.body.split(' ')),
                                                similarity=lsi_similarity_cosine[i][j]
                                                )
           )
    ReviewReleaseNoteSim.objects.bulk_create(reviewrelease_objs, batch_size=100000)
           # count = len(review.body.split(' '))
           # if lsi_similarity_cosine[i][j]>0.50 and count>20:
           #     print(lsi_similarity_cosine[i][j])
           #     print('count: ', count)
           #     print(releasenote.body)
           #     print(review.body)
           #     print('*-------------------------------------------*')
