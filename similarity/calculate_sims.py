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

store_app_id = 353263352
app_ids = ReviewReleaseNoteFlat.objects.all().order_by('store_app_id').values_list('store_app_id',flat=True).distinct()[:100]

num_topics = 300
tfidf = pickle.load( open( "exports/tfidf.p", "rb" ) )
# vectorizer = pickle.load( open( "exports/vectorizer.p", "rb" ) )
tfidf_db_map = pickle.load( open( "exports/tfidf_db_map.p", "rb" ) )
corpus_gensim = pickle.load( open( "exports/corpus_gensim.p", "rb" ) )
gensim_tfidf = list(corpus_gensim)
lsi_model = gensim.models.LsiModel.load('exports/lsi.model')

print(len(tfidf_db_map.keys()))
print(tfidf.shape)
print(len(gensim_tfidf))

for app_id in app_ids:
    print(app_id)
    lsi_releasenotes_vecs = np.zeros((1, num_topics))
    lsi_reviews_vecs = np.zeros((1, num_topics))
    releasenotes = ReviewReleaseNoteFlat.objects.filter(store_app_id=app_id, is_review=False).order_by('id')
    reviews = ReviewReleaseNoteFlat.objects.filter(store_app_id=app_id, is_review=True).order_by('id')
    count = 0
    for doc in releasenotes:
        index = tfidf_db_map[doc.id]
        lsi_releasenotes_vecs = np.vstack((lsi_releasenotes_vecs, gensim.matutils.corpus2dense(lsi_model[[gensim_tfidf[index]]], num_topics).T))
        count += 1
    lsi_releasenotes_vecs = np.delete(lsi_releasenotes_vecs,0,0)

    count = 0
    for doc in reviews:
        index = tfidf_db_map[doc.id]
        lsi_reviews_vecs = np.vstack((lsi_reviews_vecs, gensim.matutils.corpus2dense(lsi_model[[gensim_tfidf[index]]], num_topics).T))
        count += 1

    lsi_reviews_vecs = np.delete(lsi_reviews_vecs,0,0)

    lsi_similarity_cosine = cosine_similarity(lsi_reviews_vecs, lsi_releasenotes_vecs)

    print(releasenotes.count()+reviews.count())
    print('rn', releasenotes.count(), lsi_releasenotes_vecs.shape)
    print('rv', reviews.count(), lsi_reviews_vecs.shape)
    print(lsi_similarity_cosine.shape)


    for j, releasenote in enumerate(releasenotes):
       for i, review in enumerate(reviews):
           ReviewReleaseNoteSim.objects.create(store_app_id=store_app_id,
                                               releasenote=releasenote,
                                               review=review,
                                               star_rating=review.star_rating,
                                               user_apple_id=review.user_apple_id,
                                               version=releasenote.version,
                                               date=review.date,
                                               word_count=len(review.body.split(' ')),
                                               similarity=lsi_similarity_cosine[i][j]
                                               )
           # count = len(review.body.split(' '))
           # if lsi_similarity_cosine[i][j]>0.50 and count>20:
           #     print(lsi_similarity_cosine[i][j])
           #     print('count: ', count)
           #     print(releasenote.body)
           #     print(review.body)
           #     print('*-------------------------------------------*')

