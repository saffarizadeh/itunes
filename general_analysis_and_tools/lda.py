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



for app_id in app_ids:
  app = App.objects.get(store_app_id=app_id)
  release_notes = ReleaseNote.objects.filter(app=app).order_by('date')
  release_notes = [release_notes[0], release_notes[1]]
  for index, release_note in enumerate(release_notes):
    date = release_note.date
    if index != 0:
      row_num += 1
      topics = ''

      sentences = ReviewFlat.objects.filter(store_app_id=app_id, date__range=(previous_date, date)).exclude(body=None).values_list('title','body')
      tagged_sentences = stanford_pos_tag.tag_sents(sentences)
      new_sentences = []
      for sentence in tagged_sentences:
        words = [word[0] for word in sentence if word[1] in ['NN', 'NNS', 'NNP', 'RB', 'JJ', 'VB', 'VBG']]
        new_sentences.append(' '.join(words))
      # print('Checking the spellings...')
      # sentences = [TextBlob(sentence).correct() for sentence in sentences]
      # print('Spell Check Done!')
      # tokenizer = TweetTokenizer(preserve_case=False)
      # text = []
      # for sentence in sentences:
      #   this_sentence = ''
      #   tokens = tokenizer.tokenize(sentence)
      #   tagged = nltk.pos_tag(tokens)
      #   for word in tagged:
      #     if word[1] == 'NN':
      #       this_sentence += word[0] + ' '
      #   print(this_sentence)
      #   text.append(this_sentence)

      vectorizer = TfidfVectorizer(ngram_range=(1, 3), token_pattern=r'\b[a-z]+\b', min_df=1, lowercase=True, strip_accents='ascii', stop_words='english')
      topicvector = vectorizer.fit_transform(new_sentences)
      print(topicvector.shape)
      vocab = vectorizer.get_feature_names()

      """ Gensim """
      topicfeature=np.array(vectorizer.get_feature_names())
      name=list(topicfeature) #name is a list that includs all words
      numofwords=topicvector.shape[1] #total number of words
      corpus_gensim = matutils.Sparse2Corpus(topicvector.T)
      vocab_gensim = {val:key for key,val in vectorizer.vocabulary_.items()}
      start_time = time.time()
      topicnum=25

      model = ldamodel.LdaModel(corpus_gensim,id2word=vocab_gensim,num_topics=topicnum,passes=10)
      print("--- %s seconds ---" % (time.time() - start_time))

      allfeatureprob=model.show_topics(num_topics=topicnum, num_words=numofwords, formatted=False)
      wordsprob=dict()
      for i in range(topicnum):
        wordsprob[i]=dict()
        for j in range(numofwords):
          feature=allfeatureprob[i][1][j][0]
          #print(feature)
          prob=allfeatureprob[i][1][j][1]
          wordsprob[i][feature]=prob

      wordscore=dict()
      for i in range(topicnum):
        wordscore[i] = Counter()
        for feature in name:
          probsum=0
          for j in range(topicnum):
            probsum += wordsprob[j][feature]
          wordscore[i][feature]=log(wordsprob[i][feature])-log(1.0*probsum/topicnum)

      # for i in range(topicnum):
      #   sorted_x = sorted(wordscore[i].items(), key=operator.itemgetter(1), reverse=True)
      #   print(sorted_x[:40])
      #   sorted_x = wordscore[i].most_common(40)
      #   print(sorted_x[:40])
      #   words = str([word for word, prob in sorted_x[:40]])
      #   topics += 'Topic {}: {}'.format(i+1, words) + '\n'

      topics = ''
      for topic in model.show_topics(num_topics=topicnum, num_words=20, formatted=False):
        topic_id = topic[0]
        row = topic[1]
        words = [word[0] for word in row]
        topics += 'Topic {}: {}'.format(topic_id+1, words) + '\n'
        print(topics)
      # for topic_id in range(topicnum):
      #   model.get_topic_terms(topicid=i, topn=40)
      #   words =



      # print("\n\n\n\n\n")
      # for i in range(topicnum):
      #   print(model.get_topic_terms(topicid=i, topn=40))
      # print("\n\n\n\n\n")
      # print(model.get_document_topics(bow=0,minimum_probability=0.5))

      """ /Gensim """


      # n_topics = 20
      # # model = lda(n_topics=n_topics, learning_method='online', )
      # model = NMF(n_components=n_topics, random_state=1)#, alpha=.1, l1_ratio=.5)
      # model.fit(topicvector)
      # topic_word = model.components_
      # n_top_words = 40
      #
      # for i, topic_dist in enumerate(topic_word):
      #   topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
      #   topics += 'Topic {}: {}'.format(i, ' '.join(topic_words)) + '\n'


      worksheet.write(row_num, 0, app.store_app_id)
      worksheet.write(row_num, 1, app.name)
      worksheet.write(row_num, 2, date.strftime("%Y-%m-%d"))
      worksheet.write(row_num, 3, previous_date.strftime("%Y-%m-%d"))
      worksheet.write(row_num, 4, release_note.note)
      worksheet.write(row_num, 5, topics)
    previous_date = date
workbook.close()






#
# sentences = ReviewFlat.objects.all().exclude(body=None)[:50000].values_list('body', flat=True)
#
# """ Combination in a single module """
# vectorizer = TfidfVectorizer(min_df=1, stop_words='english')
# vectorizer.fit_transform(sentences)
# X_3 = vectorizer.fit_transform(sentences)
# print(X_3.shape)
# vocab = vectorizer.get_feature_names()
# pickle.dump( X_3, open( "vocab.p", "wb" ) )
# pickle.dump( X_3, open( "X_3.p", "wb" ) )
#
# # vocab = pickle.load( open( "vocab.p", "rb" ) )
# # X_3 = pickle.load( open( "X_3.p", "rb" ) )
#
#
# model = lda(n_topics=10, learning_method='online', )
# model.fit(X_3)
# print(model.components_)
# print(len(model.components_))
#
# topic_word = model.components_
# n_top_words = 10
# for i, topic_dist in enumerate(topic_word):
#   topic_words = np.array(vocab)[np.argsort(topic_dist)][:-(n_top_words+1):-1]
#   print('Topic {}: {}'.format(i, ' '.join(topic_words)))





# X_3 = pickle.load( open( "X_3.p", "rb" ) )
# X_3 = X_3.toarray()
# from sklearn.decomposition import PCA
# pca = PCA(n_components=2)
# X_r = pca.fit_transform(X_3)
# print(X_r.shape)
# print('explained variance ratio (first 20 components): %s'
#       % str(pca.explained_variance_ratio_))

# print("Performing dimensionality reduction using LSA")
# t0 = time()
# # Vectorizer results are normalized, which makes KMeans behave as
# # spherical k-means for better results. Since LSA/SVD results are
# # not normalized, we have to redo the normalization.
# svd = TruncatedSVD()
# normalizer = Normalizer(copy=False)
# lsa = make_pipeline(svd, normalizer)
# X = lsa.fit_transform(X_3)
# print(X.shape)
# print("done in %fs" % (time() - t0))
#
# explained_variance = svd.explained_variance_ratio_.sum()
# print("Explained variance of the SVD step: {}%".format(
#     int(explained_variance * 100)))
#
# print()