#!/usr/bin/env python
# coding=utf-8

import re
import jieba
from gensim import corpora, models
import numpy as np

doc = """心愿
湖水是你的眼神
梦想满天星辰
心情是一个传说
亘古不变地等候
成长是一扇树叶的门
童年有一群亲爱的人
春天是一段路程
沧海桑田的拥有
那些我爱的人
那些离逝的风
那些永远的誓言一遍一遍
那些爱我的人
那些沉淀的泪
那些永远的誓言一遍一遍
湖水是你的眼神
梦想满天星辰
心情是一个传说
亘古不变地等候
成长是一扇树叶的门
童年有一群亲爱的人
春天是一段路程
沧海桑田的拥有
那些我爱的人
那些离逝的风
那些永远的誓言一遍一遍
那些爱我的人
那些沉淀的泪
那些永远的誓言一遍一遍
我们都曾有过一张天真而忧伤的脸
手握阳光我们望着遥远
轻轻的一天天一年又一年
长大间我们是否还会再唱起心愿
轻轻的一天天一年又一年
长大间我们是否还会再唱起心愿
长大间我们是否还会再唱起心愿"""

# 对文本进行清洗和分词
doc = re.sub(u'[^\u4e00-\u9fa5]', u' ', doc)
doc = jieba.lcut(doc, cut_all=False)

# 载入语料词典
dictionary = corpora.Dictionary.load('/tmp/lyrics.dict')
# 载入语料向量
corpus = corpora.MmCorpus('/tmp/lyrics.mm')

# 计算语料的 tfidf
tfidf = models.TfidfModel(corpus)


vec_bow = dictionary.doc2bow(doc)
w2v = models.Word2Vec.load('Chinese_Word2Vec/Word60.model')

doc_vec = np.zeros(60)

for word in tfidf[vec_bow]:
    doc_vec += word[1] * w2v[dictionary[word[0]]]

lyrics_vec = []

import json

with open('lyrics.json_processed_jieba_tfidf_wrd2vec') as f_read:
    for line in f_read:
        lyrics_vec.append(json.loads(line))
        
lyrics_sim = {}

from scipy import spatial

for item in lyrics_vec:
    lyrics_sim[item['id']] = 1-spatial.distance.cosine(doc_vec, item['lyrics_vec'])

import operator

sorted_array2 = sorted(lyrics_sim.items(), key=operator.itemgetter(1), reverse=True)

k = 5

print(sorted_array2[:k])


