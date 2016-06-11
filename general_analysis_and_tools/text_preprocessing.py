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
from app.models import ReviewFlat, ReleaseNote

from nltk.tokenize import TweetTokenizer
from nltk.tokenize import MWETokenizer
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
import nltk
from nltk.corpus import wordnet

def k_tokenizer(text):
    text = text.encode('ascii',errors='ignore').replace('-', '')
    """ We should use a better way to remove non-english words """

    tokenizer = TweetTokenizer(preserve_case=False)
    tokens = tokenizer.tokenize(text)

    # stopset = set(stopwords.words('english'))
    # tokens = [word for word in tokens if not word in stopset]

    """ Synonyms using wordnet """

    mwe_tokenizer = MWETokenizer([('ios', '9'),])
    mwe_tokens = mwe_tokenizer.tokenize(tokens)

    """ We might want to tokenize by sentence and then tag each sentence and aggregate the results """

    """ train -> train_NN train_V"""
    tagged = nltk.pos_tag(mwe_tokens)

    def get_wordnet_pos(treebank_tag):

        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN # we preserve the original form of any unknown word

    wordnet_lemmatizer = WordNetLemmatizer()
    final_doc=[]
    for token, tag in tagged:
        word = tag + '_' + wordnet_lemmatizer.lemmatize(token, get_wordnet_pos(tag))
        final_doc.append(word)

    # porter = PorterStemmer()
    # final_doc=[]
    # for token in mwe_tokens:
    #     final_doc.append(porter.stem(token))

    return final_doc