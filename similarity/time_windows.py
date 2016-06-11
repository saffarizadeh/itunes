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


