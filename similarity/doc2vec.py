# -*- coding: utf-8 -*-

import gensim
from gensim.models import Doc2Vec
import random
from sklearn.cross_validation import train_test_split
import numpy as np
import pickle
from string import punctuation
import multiprocessing
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import pairwise_distances
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models.doc2vec import LabeledSentence
from gensim.models.word2vec import Word2Vec
from nltk.corpus import stopwords
import re
import xlsxwriter
import gc

row_num = 0
workbook = xlsxwriter.Workbook('similarity_report_euc_1.xlsx',{'nan_inf_to_errors': True})
worksheet = workbook.add_worksheet()

date_format_str = 'dd/mm/yyyy'
date_format = workbook.add_format({'num_format': date_format_str})
worksheet.write(row_num, 0, 'app_id')
worksheet.write(row_num, 1, 'review')
worksheet.write(row_num, 2, 'release_note')
worksheet.write(row_num, 3, 'similarity')



size = 300

def cleanText2(corpus):
    corpus = [z.lower().replace('\n','') for z in corpus]
    for c in punctuation:
        corpus = [z.replace(c, ' ') for z in corpus]
    corpus = [z.split() for z in corpus]
    return corpus

contractions = re.compile(r"'|-|\"")
# all non alphanumeric
symbols = re.compile(r'(\W+)', re.U)
# single character removal
singles = re.compile(r'(\s\S\s)', re.I|re.U)
# separators (any whitespace)
seps = re.compile(r'\s+')
punc = re.compile('[%s]' % re.escape(punctuation))

# cleaner (order matters)
def cleanText(corpus):
    new_corpus = []
    if corpus:
        for text in corpus:
            if text:
                text = text.lower()
                text = contractions.sub('', text)
                text = symbols.sub(r' \1 ', text)
                text = singles.sub(' ', text)
                text = seps.sub(' ', text)
                text = punc.sub('', text)
                #~ words = re.findall(r'[a-z]+', text)
                #~ new_corpus.append([word for word in words if word not in stopwords.words('english')])
                new_corpus.append(re.findall(r'[a-z]+', text))
            else:
                new_corpus.append('')
    return new_corpus

def nocleanText(corpus):
    new_corpus = []
    if corpus:
        for text in corpus:
            if text:
                text = text.lower()
                # text = contractions.sub(' ', text)
                text = symbols.sub(r' \1 ', text)
                text = seps.sub(' ', text)
                new_corpus.append(re.findall(r'\S+', text))
            else:
                new_corpus.append('')
    return new_corpus

def labelizeReviews(reviews, label_type):
    labelized = []
    for i,v in enumerate(reviews):
        label = '%s_%s'%(label_type,i)
        labelized.append(LabeledSentence(v, [label]))
    return labelized

trainset = []
print('Loading apps...')
apps = pickle.load( open( "apps_all.p", "rb" ) )
print('Apps loaded.')

# """ clean release notes """
# print('Removing Dupicates From Release Notes...')
# for app_id in apps.keys():
#     vectorizer = TfidfVectorizer(min_df=1)
#     releasenotes = apps[app_id]['release_notes']
#     rn_sents = []
#     index={}
#     for i, rn in enumerate(releasenotes):
#         sents = sent_tokenize(rn.replace('\n','.'))
#         index[i] = [j for j in range(len(rn_sents), len(rn_sents)+len(sents))]
#         rn_sents.extend(sents)
#     try:
#         rn_vectors = vectorizer.fit_transform(rn_sents)
#         rn_similarity = cosine_similarity(rn_vectors,rn_vectors)
#         np.fill_diagonal(rn_similarity, 0)
#         #~ rn_similarity = np.triu(rn_similarity)
#         where = np.where(rn_similarity>0.8)
#         similar_rn_reviews =list(set(where[0]))
#
#         new_rns = []
#         for sent_index in index.values():
#             rn = '. '.join([rn_sents[sent] for sent in sent_index if sent not in similar_rn_reviews])
#             new_rns.append(rn)
#         apps[app_id]['release_notes'] = new_rns
#     except:
#         pass
#
# """ train the model """
# print('Cleaning Text...')
# for app_id in apps.keys():
#     reviews = apps[app_id]['reviews']
#     if len(reviews):
#         reviews = nocleanText(reviews)
#         releasenotes = apps[app_id]['release_notes']
#         releasenotes = nocleanText(releasenotes)
#         reviews_train = labelizeReviews(reviews, 'REVIEW_%d'%(app_id))
#         releasenotes_train = labelizeReviews(releasenotes, 'RELEASENOTE_%d'%(app_id))
#         trainset.extend(reviews_train+releasenotes_train)
#
# print('Start initiating...')
# model = gensim.models.Doc2Vec(size=size, workers=multiprocessing.cpu_count(), alpha=0.025, min_alpha=0.025, dm=0, sample=1e-3) #(down sampling more frequent words)
#
# #model = Doc2Vec.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
# #""" how to mix pre-trained word2vecs and new model: https://groups.google.com/forum/#!topic/gensim/icSyNtCJsw8"""
# print('model initiated. \nBuilding Vocabulary...')
# model.build_vocab(trainset)
# print('Start training...')
# #for epoch in range(10):
# #    print('Training: pass %d'%(epoch))
# #    random.shuffle(trainset)
# #    model.train(trainset)
# for epoch in range(10):
#     print('Training: pass %d'%(epoch))
#     model.train(trainset)
#     model.alpha -= 0.002  # decrease the learning rate
#     model.min_alpha = model.alpha  # fix the learning rate, no decay
#
# model.save('Doc2Vec_all.model')
# print('model trained.')
#
""" get vectors """
print('Loading the model...')
model = Doc2Vec.load('Doc2Vec_all.model')
print('Model loaded!')
print('Extracting vectors...')
for app_id in list(apps.keys())[:10000]:
    reviews_vecs = []
    releasenotes_vecs = []
    reviews_len = len(apps[app_id]['reviews'])
    if reviews_len:
        releasenotes_len = len(apps[app_id]['release_notes'])
        for i in range(reviews_len):
            reviews_vecs.append(np.array(model.docvecs['REVIEW_%d_%d'%(app_id, i)]).reshape((1, size)))
        for i in range(releasenotes_len):
            releasenotes_vecs.append(np.array(model.docvecs['RELEASENOTE_%d_%d'%(app_id, i)]).reshape((1, size)))
        apps[app_id]['reviews_vecs'] = reviews_vecs
        apps[app_id]['releasenotes_vecs'] = releasenotes_vecs
print('Vectors extracted!')
print('Saving vectors...')
pickle.dump(apps, open('apps_and_vecs.p','wb'))
print('Vectors saved!')

print('Loading Vectors...')
apps_vecs = pickle.load(open('apps_and_vecs.p','rb'))
print('Vectors Loaded!')

# release_notes_mat = np.array(apps[307906541]['releasenotes_vecs']).reshape((len(apps[307906541]['releasenotes_vecs']), size))
# reviews_mat = np.array(apps[307906541]['reviews_vecs']).reshape((len(apps[307906541]['reviews_vecs']), size))
#
# similarity = cosine_similarity(reviews_mat,release_notes_mat)
#
# """testing wheather similarity matrix is calculated correctly"""
# print(similarity[0][0])
# Z = np.dot(reviews_mat[0],release_notes_mat[0].T)/(np.linalg.norm(reviews_mat[0])*np.linalg.norm(release_notes_mat[0]))
# print(Z)
#
# """ find conncetions (similar reviews and release notes) """
# where = np.where(similarity>0.5)
# similar_rn_reviews = zip(where[0],where[1])
# for rn_reviews in similar_rn_reviews:
#     review = rn_reviews[0]
#     rn = rn_reviews[1]
#     print('{',  apps[307906541]['release_notes'][rn], '\n\n', apps[307906541]['reviews'][review] ,'}')


print('Creating the report...')
for app_id in list(apps.keys())[:10000]:
    reviews_len = len(apps_vecs[app_id]['reviews'])
    if reviews_len:
        release_notes_mat = np.array(apps_vecs[app_id]['releasenotes_vecs']).reshape(
            (len(apps_vecs[app_id]['releasenotes_vecs']), size))
        reviews_mat = np.array(apps_vecs[app_id]['reviews_vecs']).reshape((len(apps_vecs[app_id]['reviews_vecs']), size))
        # similarity = cosine_similarity(reviews_mat, release_notes_mat)
        similarity = pairwise_distances(reviews_mat, release_notes_mat, metric='euclidean')
        releasenotes = apps_vecs[app_id]['release_notes']
        reviews = apps_vecs[app_id]['reviews']
        for j, release_note in enumerate(releasenotes):
            for i, review in enumerate(reviews):
                row_num += 1
                worksheet.write(row_num, 0, app_id)
                worksheet.write(row_num, 1, review)
                worksheet.write(row_num, 2, release_note)
                worksheet.write(row_num, 3, similarity[i][j])
workbook.close()
print('Report created!')

