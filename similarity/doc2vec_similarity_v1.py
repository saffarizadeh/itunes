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

print('Loading the model...')
doc2vec_model = Doc2Vec.load('Doc2Vec_0.model')
print('Model loaded!')

size = 100

doc2vec_releasenotes_vecs = np.zeros((1,size))
doc2vec_reviews_vecs = np.zeros((1,size))

releasenotes = ReviewReleaseNoteFlat.objects.filter(store_app_id__in=[353263352], is_review=False).order_by('id')
reviews = ReviewReleaseNoteFlat.objects.filter(store_app_id__in=[353263352], is_review=True).order_by('id')

for doc in releasenotes:
    doc2vec_releasenotes_vecs = np.vstack((doc2vec_releasenotes_vecs, np.array(doc2vec_model.docvecs[doc.id-2207805]).reshape((1, size))))

doc2vec_releasenotes_vecs = np.delete(doc2vec_releasenotes_vecs, 0, 0)

for doc in reviews:
    doc2vec_reviews_vecs = np.vstack((doc2vec_reviews_vecs, np.array(doc2vec_model.docvecs[doc.id - 2207805]).reshape((1, size))))

doc2vec_reviews_vecs = np.delete(doc2vec_reviews_vecs,0,0)

doc2vec_similarity_cosine = cosine_similarity(doc2vec_reviews_vecs, doc2vec_releasenotes_vecs)
doc2vec_similarity_euc = pairwise_distances(doc2vec_reviews_vecs, doc2vec_releasenotes_vecs, metric='euclidean')



################################
num_topics = 100
tfidf = pickle.load( open( "tfidf.p", "rb" ) )
corpus_gensim = pickle.load( open( "corpus_gensim.p", "rb" ) )
gensim_tfidf = list(corpus_gensim)

tfidf_releasenotes_vecs = None
tfidf_reviews_vecs = None

lda_model = gensim.models.LdaModel.load('lda.model')
lda_releasenotes_vecs = np.zeros((1,num_topics))
lda_reviews_vecs = np.zeros((1,num_topics))

lsi_model = gensim.models.LsiModel.load('lsi.model')
lsi_releasenotes_vecs = np.zeros((1,num_topics))
lsi_reviews_vecs = np.zeros((1,num_topics))

count = 0
for doc in releasenotes:
    if gensim_tfidf[doc.id - 3717281]:
        lda_releasenotes_vecs = np.vstack((lda_releasenotes_vecs, gensim.matutils.corpus2dense(lda_model[[gensim_tfidf[doc.id-3717281]]],num_topics).T))
    else:
        lda_releasenotes_vecs = np.vstack((lda_releasenotes_vecs,np.zeros((1,num_topics))))
    lsi_releasenotes_vecs = np.vstack((lsi_releasenotes_vecs, gensim.matutils.corpus2dense(lsi_model[[gensim_tfidf[doc.id - 3717281]]], num_topics).T))
    if count == 0:
        tfidf_releasenotes_vecs = tfidf[doc.id - 3717281]
    else:
        tfidf_releasenotes_vecs = sparse_vstack((tfidf_releasenotes_vecs, tfidf[doc.id - 3717281]))
    count += 1

lda_releasenotes_vecs = np.delete(lda_releasenotes_vecs,0,0)
lsi_releasenotes_vecs = np.delete(lsi_releasenotes_vecs,0,0)

count = 0
for doc in reviews:
    if gensim_tfidf[doc.id - 3717281]:
        lda_reviews_vecs = np.vstack((lda_reviews_vecs, gensim.matutils.corpus2dense(lda_model[[gensim_tfidf[doc.id - 3717281]]], num_topics).T))
        # we could send the whole corpus of this app_id to the model in one step
    else:
        lda_reviews_vecs = np.vstack((lda_reviews_vecs, np.zeros((1, num_topics))))
    lsi_reviews_vecs = np.vstack((lsi_reviews_vecs, gensim.matutils.corpus2dense(lsi_model[[gensim_tfidf[doc.id - 3717281]]], num_topics).T))
    if count == 0:
        tfidf_reviews_vecs = tfidf[doc.id - 3717281]
    else:
        tfidf_reviews_vecs = sparse_vstack((tfidf_reviews_vecs, tfidf[doc.id - 3717281]))
    count += 1

lda_reviews_vecs = np.delete(lda_reviews_vecs,0,0)
lsi_reviews_vecs = np.delete(lsi_reviews_vecs,0,0)

tfidf_similarity_cosine = cosine_similarity(tfidf_reviews_vecs, tfidf_releasenotes_vecs)
tfidf_similarity_euc = pairwise_distances(tfidf_reviews_vecs, tfidf_releasenotes_vecs, metric='euclidean')

lda_similarity_cosine = cosine_similarity(lda_reviews_vecs, lda_releasenotes_vecs)
lda_similarity_euc = pairwise_distances(lda_reviews_vecs, lda_releasenotes_vecs, metric='euclidean')

lsi_similarity_cosine = cosine_similarity(lsi_reviews_vecs, lsi_releasenotes_vecs)
lsi_similarity_euc = pairwise_distances(lsi_reviews_vecs, lsi_releasenotes_vecs, metric='euclidean')


################################

row_num = 2
workbook = xlsxwriter.Workbook('similarity_report_all_1.xlsx',{'nan_inf_to_errors': True})
worksheet = workbook.add_worksheet()

date_format_str = 'dd/mm/yyyy'
date_format = workbook.add_format({'num_format': date_format_str})
worksheet.write(row_num, 0, 'id')
worksheet.write(row_num, 1, 'app_id')
worksheet.write(row_num, 2, 'rating')
worksheet.write(row_num, 3, 'review')

for j, release_note in enumerate(releasenotes):
    row_num = 0
    worksheet.merge_range(row_num, 9*j+4, row_num, 9*j+12, release_note.body)
    row_num = 1
    worksheet.merge_range(row_num, 9*j+4, row_num, 9*j+5, 'Doc2Vec')
    worksheet.merge_range(row_num, 9*j+6, row_num, 9*j+7, 'LDA')
    worksheet.merge_range(row_num, 9*j+8, row_num, 9*j+9, 'LSA')
    worksheet.merge_range(row_num, 9*j+10, row_num, 9*j+11, 'TfIdf')
    worksheet.write(row_num, 9*j+12, 'Manual Coding')
    row_num = 2
    worksheet.write(row_num, 9*j+4, 'Cosine')
    worksheet.write(row_num, 9*j+5, 'Euclidean')
    worksheet.write(row_num, 9*j+6, 'Cosine')
    worksheet.write(row_num, 9*j+7, 'Euclidean')
    worksheet.write(row_num, 9*j+8, 'Cosine')
    worksheet.write(row_num, 9*j+9, 'Euclidean')
    worksheet.write(row_num, 9*j+10, 'Cosine')
    worksheet.write(row_num, 9*j+11, 'Euclidean')
    worksheet.write(row_num, 9*j+12, 'Manual Score')
    for i, review in enumerate(reviews):
        row_num += 1
        worksheet.write(row_num, 0, review.id)
        worksheet.write(row_num, 1, review.store_app_id)
        worksheet.write(row_num, 2, review.star_rating)
        worksheet.write(row_num, 3, review.body)
        worksheet.write(row_num, 9*j+4, doc2vec_similarity_cosine[i][j])
        worksheet.write(row_num, 9*j+5, doc2vec_similarity_euc[i][j])
        worksheet.write(row_num, 9*j+6, lda_similarity_cosine[i][j])
        worksheet.write(row_num, 9*j+7, lda_similarity_euc[i][j])
        worksheet.write(row_num, 9*j+8, lsi_similarity_cosine[i][j])
        worksheet.write(row_num, 9*j+9, lsi_similarity_euc[i][j])
        worksheet.write(row_num, 9*j+10, tfidf_similarity_cosine[i][j])
        worksheet.write(row_num, 9*j+11, tfidf_similarity_euc[i][j])

workbook.close()
print('Report created!')