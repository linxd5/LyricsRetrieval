#!/usr/bin/env python
# coding=utf-8

from preprocess_json import preprocess
from jieba_seg import jieba_seg
from tfidf_gensim import tfidf_gensim
from wrd2vec import wrd2vec

if __name__ == '__main__':
    file = 'lyrics.json'

    file = preprocess(file)
    file = jieba_seg(file)
    file = tfidf_gensim(file)
    file = wrd2vec(file)

