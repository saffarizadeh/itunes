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


import gensim
import random
from sklearn.cross_validation import train_test_split
import numpy as np
import pickle
from string import punctuation
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import pairwise_distances
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import re
import xlsxwriter
from collections import OrderedDict
import multiprocessing
from collections import namedtuple
from contextlib import contextmanager
from timeit import default_timer
import time
from random import shuffle
import datetime
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from gensim import matutils
from gensim import models, similarities
from gensim.similarities import MatrixSimilarity, SparseMatrixSimilarity, Similarity
import gc
from nltk.tokenize import TweetTokenizer

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

def tokenize_lemmatizer(text):
    if text:
        text = punc.sub('', text)
        return [lemmatizer.lemmatizer(token) for token in tokenizer.tokenize(gensim.utils.to_unicode(text))]
    else:
        return []

class CleanDocuments(object):
    def __iter__(self):
        for document in list(ReviewReleaseNoteFlat.objects.filter(store_app_id=353263352).order_by('id')): #id >= 3717281
            yield document.body


vectorizer = TfidfVectorizer(ngram_range=(1, 3), tokenizer=tokenize_stemmer, min_df=2, max_df=0.8, lowercase=True, strip_accents='ascii', stop_words='english')
tfidf = vectorizer.fit_transform(CleanDocuments())
print('Saving tfidf...')
pickle.dump(tfidf, open('tfidf.p','wb'))
print('tfidf saved!')


corpus_gensim = matutils.Sparse2Corpus(tfidf.T)
del(tfidf)
print('Saving corpus_gensim...')
pickle.dump(corpus_gensim, open('corpus_gensim.p','wb'))
print('corpus_gensim saved!')

vocab_gensim = {val: key for key, val in vectorizer.vocabulary_.items()} #gensim requires {id:word} dict not {word:id}
print('Saving vocab_gensim...')
pickle.dump(vocab_gensim, open('vocab_gensim.p','wb'))
print('vocab_gensim saved!')

# tfidf = pickle.load( open( "tfidf.p", "rb" ) )
# corpus_gensim = pickle.load( open( "corpus_gensim.p", "rb" ) )
# gensim_tfidf = list(corpus_gensim)
# vocab_gensim = pickle.load( open( "vocab_gensim.p", "rb" ) )

num_topics = 100

gc.collect()
lsi = models.LsiModel(corpus_gensim, id2word=vocab_gensim, num_topics=num_topics)
print('Saving lsi_model...')
lsi.save('lsi.model')
print('lsi_model saved!')
# lsi_matrix = gensim.matutils.corpus2dense(lsi[corpus_gensim], len(lsi.projection.s)).T / lsi.projection.s
# print('Saving lsi_matrix...')
# pickle.dump(lsi_matrix, open('lsi_matrix.p','wb'))
# print('lsi_matrix saved!')

gc.collect()

# lda = models.LdaModel(corpus_gensim, id2word=vocab_gensim, num_topics=num_topics, passes=5)
lda = models.ldamulticore.LdaMulticore(corpus_gensim, id2word=vocab_gensim, num_topics=num_topics, passes=5)#, alpha='auto') #auto needs non multicore LDA
print('Saving lda_model...')
lda.save('lda.model')
print('lda_model saved!')
# lda_matrix = gensim.matutils.corpus2dense(lda[corpus_gensim], lda.num_topics)
# print('Saving lda_matrix...')
# pickle.dump(lda_matrix, open('lda_matrix.p','wb'))
# print('lda_matrix saved!')



"""
    To avoid memory problem we should use built-in methods instead of using numpy arrays.
    for example: http://radimrehurek.com/topic_modeling_tutorial/3%20-%20Indexing%20and%20Retrieval.html
    Note: num_features is the number of dimensions.
"""

# index = Similarity(lda[corpus_gensim], num_features=lda.num_topics)
# index = Similarity(corpus_gensim, num_features=400)