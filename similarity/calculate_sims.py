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
from gensim.models.doc2vec import LabeledSentence
from gensim.models.word2vec import Word2Vec
from nltk.corpus import stopwords
import re
import xlsxwriter
from gensim.models import Doc2Vec
import gensim.models.doc2vec
from collections import OrderedDict
import multiprocessing
import gensim
from gensim.models.doc2vec import TaggedDocument
from collections import namedtuple
from contextlib import contextmanager
from timeit import default_timer
import time
from gensim.test.test_doc2vec import ConcatenatedDoc2Vec
from random import shuffle
import datetime
import gensim
from sklearn.metrics.pairwise import linear_kernel
from scipy.sparse import vstack as sparse_vstack


size = 100

releasenotes = ReviewReleaseNoteFlat.objects.filter(store_app_id__in=[353263352], is_review=False).order_by('id')
reviews = ReviewReleaseNoteFlat.objects.filter(store_app_id__in=[353263352], is_review=True).order_by('id')


################################
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
