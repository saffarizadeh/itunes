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

@contextmanager
def elapsed_timer():
    start = default_timer()
    elapser = lambda: default_timer() - start
    yield lambda: elapser()
    end = default_timer()
    elapser = lambda: end-start


cores = multiprocessing.cpu_count()
assert gensim.models.doc2vec.FAST_VERSION > -1, "this will be painfully slow otherwise"

from nltk.tokenize import TweetTokenizer

tokenizer = TweetTokenizer()

def clean_tokenize(text):
    if text:
        return tokenizer.tokenize(gensim.utils.to_unicode(text).lower())
    else:
        return []

class TaggedDocuments(object):
    def __iter__(self):
        for document in list(ReviewReleaseNoteFlat.objects.all().order_by('id')):
            yield TaggedDocument(clean_tokenize(document.body), [document.id-2207805])


alldocs = list(TaggedDocuments()) #list() will force python to calculate all elements. It is good when we want to store the results of every step.
print('Saving alldocs...')
pickle.dump(alldocs, open('alldocs.p','wb'))
print('alldocs saved!')

# print('Loading alldocs...')
# alldocs = pickle.load(open('alldocs.p','rb'))
# print('alldocs loaded!')

doc_list = alldocs[:]
print(alldocs[:10])

size = 100
simple_models = [
    # PV-DM w/concatenation - window=5 (both sides) approximates paper's 10-word total window size
    # Doc2Vec(dm=1, dm_concat=1, size=size, window=5, negative=5, hs=0, min_count=2, workers=cores),
    # PV-DBOW
    Doc2Vec(dm=0, size=size, negative=5, hs=0, min_count=2, workers=cores),
    # PV-DM w/average
    # Doc2Vec(dm=1, dm_mean=1, size=size, window=10, negative=5, hs=0, min_count=2, workers=cores),
]

simple_models[0].build_vocab(alldocs)
print(simple_models[0])

for model in simple_models[1:]:
    model.reset_from(simple_models[0])
    print(model)

models_by_name = OrderedDict((str(model), model) for model in simple_models)

# models_by_name['dbow+dmm'] = ConcatenatedDoc2Vec([simple_models[1], simple_models[2]])
# models_by_name['dbow+dmc'] = ConcatenatedDoc2Vec([simple_models[1], simple_models[0]])

alpha, min_alpha, passes = (0.025, 0.001, 10) #20)
alpha_delta = (alpha - min_alpha) / passes

print("START %s" % datetime.datetime.now())

for epoch in range(passes):
    shuffle(doc_list)  # shuffling gets best results

    for name, train_model in models_by_name.items():
        # train
        duration = 'na'
        train_model.alpha, train_model.min_alpha = alpha, alpha
        with elapsed_timer() as elapsed:
            train_model.train(doc_list)
            duration = '%.1f' % elapsed()

    print('completed pass %i at alpha %f' % (epoch + 1, alpha))
    alpha -= alpha_delta

print("END %s" % str(datetime.datetime.now()))

model = simple_models[0]  # model = random.choice(simple_models)
model.save('Doc2Vec_0.model')
print('model trained and saved!')

doc_id = np.random.randint(simple_models[0].docvecs.count)
print(doc_id)
print('vectors count: ', simple_models[0].docvecs.count)
print('docs count: ', len(alldocs))

sims = model.docvecs.most_similar(doc_id, topn=100)
print(u'TARGET (%d): «%s»\n' % (doc_id, ' '.join(alldocs[doc_id].words)))
print(u'SIMILAR/DISSIMILAR DOCS PER MODEL %s:\n' % model)
for label, index in [('MOST', 0), ('MEDIAN', len(sims)//2), ('LEAST', len(sims) - 1)]:
    print(u'%s %s: «%s»\n' % (label, sims[index], ' '.join(alldocs[sims[index][0]].words)))


# model = Doc2Vec(dm=1, dm_concat=1, size=size, window=5, negative=5, hs=0, min_count=2, workers=cores)
# model.build_vocab(alldocs)
# model.train(alldocs)
# print(model.docvecs.count)

