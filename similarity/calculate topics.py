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
import operator

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

# app_ids = ReviewReleaseNoteFlat.objects.all().order_by('store_app_id').values_list('store_app_id',flat=True).distinct()
# app_ids = App.objects.filter(is_reviews_crawled=True).order_by('id').values_list('store_app_id',flat=True)
tfidf_db_map = pickle.load( open( "exports/lda_tfidf_db_map.p", "rb" ) )
print('getting doc ids...')
doc_ids = tfidf_db_map.keys()
print(len(doc_ids))
app_ids = ReviewReleaseNoteFlat.objects.filter(id__in=doc_ids, is_review=True).order_by('store_app_id').values_list('store_app_id',flat=True).distinct()
print(len(app_ids))
print('doc ids retrieved!')

num_topics = 50
tfidf = pickle.load( open( "exports/lda_tfidf.p", "rb" ) )
# vectorizer = pickle.load( open( "exports/vectorizer.p", "rb" ) )

corpus_gensim = pickle.load( open( "exports/lda_corpus_gensim.p", "rb" ) )
gensim_tfidf = list(corpus_gensim)
lda_model = gensim.models.LdaMulticore.load('exports/lda.model')

print(len(tfidf_db_map.keys()))
print(tfidf.shape)
print(len(gensim_tfidf))

# for topic in lda_model.print_topics(num_topics=num_topics, num_words=20):
#     print(topic)

for app_id in app_ids:
    print(app_id)
    reviews = ReviewReleaseNoteFlat.objects.filter(store_app_id=app_id, is_review=True).order_by('id')
    first_review = None
    last_review = None
    try:
        first_review = reviews[0].id
        last_review = reviews.order_by('-id')[0].id
        print('First Review: ', first_review)
        print('Last Review: ', last_review)
    except:
        print('No Review!!!')
    try:
        """ more memory intensive but faster """
        first_review_index = tfidf_db_map[first_review]
        last_review_index = tfidf_db_map[last_review]
        documents = gensim_tfidf[first_review_index:last_review_index + 1]
        print(reviews.count(), len(documents))
        for index, review in enumerate(reviews):
            document = documents[index]
            top_topic = lda_model[document]
            top_topic.sort(key=operator.itemgetter(1), reverse=True)
            print('Topic: ', top_topic[0][0], 'Review: ', review.body)
        # for document in documents:
        #     doc_lda = lda_model[document]
    except:
        print('Some error: maybe no Review^')
