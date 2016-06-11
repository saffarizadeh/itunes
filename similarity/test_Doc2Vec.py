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
from time import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import make_pipeline
import pickle
from sklearn.decomposition import LatentDirichletAllocation as lda
import time
from gensim.models import ldamodel
from gensim import matutils
from math import log
from collections import Counter, defaultdict

from sklearn.decomposition import NMF

from nltk.tokenize import TweetTokenizer
import nltk
import re
import os
path = '/home/kaminem64/stanford'
os.environ['CLASSPATH'] = '%s/stanford-postagger-full-2015-04-20/stanford-postagger.jar:%s/stanford-ner-2015-04-20/stanford-ner.jar:%s/stanford-parser-full-2015-04-20/stanford-parser.jar:%s/stanford-parser-full-2015-04-20/stanford-parser-3.6.0-models.jar' %(path, path, path, path)
os.environ['STANFORD_MODELS'] = '%s/stanford-postagger-full-2015-04-20/models:%s/stanford-ner-2015-04-20/classifiers' %(path, path)
from nltk.tag.stanford import StanfordPOSTagger

stanford_pos_tag = StanfordPOSTagger('english-bidirectional-distsim.tagger')

import xlsxwriter
workbook = xlsxwriter.Workbook('topic_modeling.xlsx')
worksheet = workbook.add_worksheet()
row_num = 0
worksheet.write(row_num, 0, 'store_app_id')
worksheet.write(row_num, 1, 'name')
worksheet.write(row_num, 2, 'start_date')
worksheet.write(row_num, 3, 'end_date')
worksheet.write(row_num, 4, 'release_note')
worksheet.write(row_num, 5, 'topics')

app_ids = [307906541]#, 282614216, 383298204, 421254504, 509993510, ]
previous_date = None

from textblob import TextBlob
from nltk.stem.porter import PorterStemmer
import string
stemmer = PorterStemmer()

import operator

def stem_tokens(tokens, stemmer):
  stemmed = []
  for item in tokens:
    stemmed.append(stemmer.stem(item))
  return stemmed

def tokenize(text):
  # lowers = text.lower()
  # no_punctuation = lowers.translate(None, string.punctuation)
  time0 = time.time()
  # tokens = [word[0] for word in TextBlob(unicode(TextBlob(text).correct())).tags if word[1] in ['NN', 'NNS', 'NNP', 'JJ', 'VB'] ]
  # stems = stem_tokens(tokens, stemmer)

  stems = re.findall('[a-z]+', text)
  # stems = [word[0] for word in nltk.pos_tag(tokens) if word[1] in ['NN', 'NNS', 'NNP', 'JJ', 'VB'] ]

  print('%s seconds' % (time.time()-time0))
  print(stems)
  return stems

from gensim.models.doc2vec import TaggedDocument, Doc2Vec
from gensim.models.word2vec import Word2Vec

for app_id in app_ids:
  app = App.objects.get(store_app_id=app_id)
  release_notes = ReleaseNote.objects.filter(app=app).order_by('date')
  release_notes = [release_notes[0], release_notes[1]]
  for index, release_note in enumerate(release_notes):
    date = release_note.date
    print(date)
    if index != 0:
      row_num += 1
      topics = ''
    
      #~ pos_sentences = ReviewFlat.objects.filter(store_app_id=app_id, date__range=(previous_date, date), star_rating__gt=3).exclude(body=None).values_list('body')
      #~ tagged_pos_sentences = stanford_pos_tag.tag_sents(pos_sentences)
      #~ new_pos_sentences = []
      #~ pos_words = []
      #~ pos_documents = []
      #~ for sentence in tagged_pos_sentences:
        #~ pos_words = [word[0] for word in sentence if word[1] in ['NN', 'NNS', 'NNP', 'RB', 'JJ', 'VB', 'VBG']]
        #~ pos_documents.append(pos_words)
#~ 
      #~ neg_sentences = ReviewFlat.objects.filter(store_app_id=app_id, date__range=(previous_date, date), star_rating__lt=4).exclude(body=None).values_list('body')
      #~ tagged_neg_sentences = stanford_pos_tag.tag_sents(neg_sentences)
      #~ new_neg_sentences = []
      #~ neg_words = []
      #~ neg_documents = []
      #~ for sentence in tagged_neg_sentences:
        #~ neg_words = [word[0] for word in sentence if word[1] in ['NN', 'NNS', 'NNP', 'RB', 'JJ', 'VB', 'VBG']]
        #~ neg_documents.append(neg_words)
    

      sentences = ReviewFlat.objects.filter(store_app_id=app_id, date__range=(previous_date, date)).exclude(body=None).values_list('body')
      tagged_sentences = stanford_pos_tag.tag_sents(sentences)
      new_sentences = []
      words = []
      documents = []
      for sentence in tagged_sentences:
        words = [word[0] for word in sentence if word[1] in ['NN', 'NNS', 'NNP', 'RB', 'JJ', 'VB', 'VBG']]
        documents.append(words)
    previous_date = date
n_dim = 300
#Initialize model and build vocab
app_w2v = Word2Vec(size=n_dim, min_count=10)
app_w2v.build_vocab(documents)
app_w2v.train(documents)

def buildWordVector(text, size):
  vec = np.zeros(size).reshape((1, size))
  count = 0.
  for word in text:
	try:
	  vec += app_w2v[word].reshape((1, size))
	  count += 1.
	except KeyError:
	  continue
  if count != 0:
    vec /= count
  return vec

from sklearn.preprocessing import scale
vecs = np.concatenate([buildWordVector(z, n_dim) for z in documents])
print(vecs)
vecs = scale(vecs)
print(vecs)


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


from sklearn.cluster import KMeans
from sklearn import datasets

np.random.seed(5)

centers = [[1, 1], [-1, -1], [1, -1]]
iris = datasets.load_iris()
X = vecs
print(X)
#~ y = iris.target

estimators = {'k_means_iris_3': KMeans(n_clusters=3),
              'k_means_iris_8': KMeans(n_clusters=8),
              'k_means_iris_bad_init': KMeans(n_clusters=3, n_init=1,
                                              init='random')}


fignum = 1
for name, est in estimators.items():
    fig = plt.figure(fignum, figsize=(4, 3))
    plt.clf()
    ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)

    plt.cla()
    est.fit(X)
    labels = est.labels_

    ax.scatter(X[:, 3], X[:, 0], X[:, 2], c=labels.astype(np.float))

    ax.w_xaxis.set_ticklabels([])
    ax.w_yaxis.set_ticklabels([])
    ax.w_zaxis.set_ticklabels([])
    ax.set_xlabel('Petal width')
    ax.set_ylabel('Sepal length')
    ax.set_zlabel('Petal length')
    fignum = fignum + 1

# Plot the ground truth
fig = plt.figure(fignum, figsize=(4, 3))
plt.clf()
ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)

plt.cla()

#~ for name, label in [('Setosa', 0),
                    #~ ('Versicolour', 1),
                    #~ ('Virginica', 2)]:
    #~ ax.text3D(X[y == label, 3].mean(),
              #~ X[y == label, 0].mean() + 1.5,
              #~ X[y == label, 2].mean(), name,
              #~ horizontalalignment='center',
              #~ bbox=dict(alpha=.5, edgecolor='w', facecolor='w'))
# Reorder the labels to have colors matching the cluster results
#~ y = np.choose(y, [1, 2, 0]).astype(np.float)
ax.scatter(X[:, 3], X[:, 0], X[:, 2])#, c=y)

ax.w_xaxis.set_ticklabels([])
ax.w_yaxis.set_ticklabels([])
ax.w_zaxis.set_ticklabels([])
ax.set_xlabel('Petal width')
ax.set_ylabel('Sepal length')
ax.set_zlabel('Petal length')
plt.show()



