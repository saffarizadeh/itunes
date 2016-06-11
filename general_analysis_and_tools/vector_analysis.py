from __future__ import print_function
# -*- coding: utf-8 -*-
__author__ = 'Kambiz'

import sys
sys.path.insert(0, '/home/kaminem64/itunes')
sys.path.insert(0, '/home/kaminem64/itunes/app')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'itunes.settings'
import django
django.setup()

import numpy as np
import pickle

reverse_dictionary = pickle.load( open( "reverse_dictionary.p", "rb" ) )
final_embeddings = pickle.load( open( "final_embeddings.p", "rb" ) )
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=10, n_init=10, init='random')
clusters = kmeans.fit_transform(final_embeddings)
pickle.dump( kmeans, open( "kmeans.p", "wb" ) )
pickle.dump( clusters, open( "clusters.p", "wb" ) )

# kmeans = pickle.load( open( "kmeans.p", "rb" ) )
# clusters = pickle.load( open( "clusters.p", "rb" ) )

adict = {}
for i in set(kmeans.labels_):
    adict[i] = []
for index, j in enumerate(kmeans.labels_):
    adict[j].append(reverse_dictionary[index])
for i in set(kmeans.labels_):
    print('cluster#',i,' ',adict[i][1000:1020])

# print(type(final_embeddings), final_embeddings.shape)
# print([reverse_dictionary[i] for i in range(500)])
# seed_word = final_embeddings[254,:]
# embeddings_matrix = final_embeddings
# t = embeddings_matrix.dot(seed_word.T)
# d = np.absolute(t)
# cluster =d.argsort()[-50:][::-1]
# print([reverse_dictionary[i] for i in cluster])
# print(d.shape)
# # print(d)
