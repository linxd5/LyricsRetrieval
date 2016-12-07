#!/usr/bin/env python
# coding=utf-8

from preprocess_json import preprocess
from jieba_seg import jieba_seg
from tfidf_gensim import tfidf_gensim
from wrd2vec import wrd2vec
import time

if __name__ == '__main__':
    file = 'processed_data/lyrics_all.json'

    begin_time = time.time()

    file = preprocess(file)
    file = jieba_seg(file)
    file = tfidf_gensim(file)
    file = wrd2vec(file)

    end_time = time.time()

    print("++++ Training using ", end_time-begin_time, " s")

