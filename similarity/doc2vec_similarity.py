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


print('Loading the model...')
model = Doc2Vec.load('Doc2Vec_0.model')
print('Model loaded!')

releasenotes_vecs = []
reviews_vecs = []
size = 100

releasenotes_vecs = np.zeros((1,size))
reviews_vecs = np.zeros((1,size))

releasenotes = ReviewReleaseNoteFlat.objects.filter(store_app_id__in=[353263352], is_review=False).order_by('id')
reviews = ReviewReleaseNoteFlat.objects.filter(store_app_id__in=[353263352], is_review=True).order_by('id')

for doc in releasenotes:
    releasenotes_vecs = np.vstack((releasenotes_vecs, np.array(model.docvecs[doc.id-2207805]).reshape((1, size))))

releasenotes_vecs = np.delete(releasenotes_vecs, 0, 0)

for doc in reviews:
    reviews_vecs = np.vstack((reviews_vecs, np.array(model.docvecs[doc.id - 2207805]).reshape((1, size))))

reviews_vecs = np.delete(reviews_vecs,0,0)

similarity_cosine = cosine_similarity(reviews_vecs, releasenotes_vecs)
similarity_euc = pairwise_distances(reviews_vecs, releasenotes_vecs, metric='euclidean')


row_num = 2
workbook = xlsxwriter.Workbook('similarity_report_new_1.xlsx',{'nan_inf_to_errors': True})
worksheet = workbook.add_worksheet()

date_format_str = 'dd/mm/yyyy'
date_format = workbook.add_format({'num_format': date_format_str})
worksheet.write(row_num, 0, 'id')
worksheet.write(row_num, 1, 'app_id')
worksheet.write(row_num, 2, 'rating')
worksheet.write(row_num, 3, 'review')

for j, release_note in enumerate(releasenotes):
    row_num = 0
    worksheet.merge_range(row_num, 7*j+4, row_num, 7*j+10, release_note.body)
    row_num = 1
    worksheet.merge_range(row_num, 7*j+4, row_num, 7*j+5, 'Doc2Vec')
    worksheet.merge_range(row_num, 7*j+6, row_num, 7*j+7, 'LSA')
    worksheet.merge_range(row_num, 7*j+8, row_num, 7*j+9, 'LDA')
    worksheet.write(row_num, 7*j+10, 'Manual Coding')
    row_num = 2
    worksheet.write(row_num, 7*j+4, 'Cosine')
    worksheet.write(row_num, 7*j+5, 'Euclidean')
    worksheet.write(row_num, 7*j+6, 'Cosine')
    worksheet.write(row_num, 7*j+7, 'Euclidean')
    worksheet.write(row_num, 7*j+8, 'Cosine')
    worksheet.write(row_num, 7*j+9, 'Euclidean')
    worksheet.write(row_num, 7*j+10, 'Manual Score')
    for i, review in enumerate(reviews):
        row_num += 1
        worksheet.write(row_num, 0, review.id)
        worksheet.write(row_num, 1, review.store_app_id)
        worksheet.write(row_num, 2, review.star_rating)
        worksheet.write(row_num, 3, review.body)
        worksheet.write(row_num, 7*j+4, similarity_cosine[i][j])
        worksheet.write(row_num, 7*j+5, similarity_euc[i][j])

workbook.close()
print('Report created!')