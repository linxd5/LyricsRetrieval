#coding=utf8

import json
import os
import re
import sys
import jieba
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from gensim.models.word2vec import Word2Vec
from sklearn.metrics import euclidean_distances
from pyemd import emd
from time import time
from multiprocessing import Process
from multiprocessing import Manager

test = {}
class WMD:
    def __init__(self, w2v_model_path, w2v_len, process_nums):
        self.word2vec = Word2Vec.load_word2vec_format(w2v_model_path, binary=True)
        self.w2v_len = w2v_len
        self.lyric_corpus = []
        self.process_nums = process_nums
        self.dis = {}
        with open('lyrics_5000.txt', 'r') as f:
            for line in f.readlines():
                lyric = json.loads(line.strip())
                self.lyric_corpus.append(lyric)

    def calc_wmd(self, doc1, doc2):
        vect = CountVectorizer().fit([doc1, doc2])
        vec1, vec2 = vect.transform([doc1, doc2]) 
        vec1 = vec1.toarray().ravel()
        vec2 = vec2.toarray().ravel()
        W = []
        for w in vect.get_feature_names():
            if w in self.word2vec.vocab:
                W.append(self.word2vec[w])
            else:
                W.append(np.random.uniform(-1.0,1.0, self.w2v_len))

        D = euclidean_distances(W)
        
        # pyemd needs double precision input
        vec1 = vec1.astype(np.double)
        vec2 = vec2.astype(np.double)
        vec1 /= vec1.sum()
        vec2 /= vec2.sum()
        D = D.astype(np.double)
        D /= D.max()
        return emd(vec1, vec2, D)

    def query(self, query_lyric):
        start = time()
        manager = Manager()
        dis = manager.dict()

        query_lyric = re.sub(u'[^\u4e00-\u9fa5]', u' ', query_lyric)
        query_lyric = jieba.lcut(query_lyric, cut_all=False)
        process = []
        block_size = len(self.lyric_corpus) / self.process_nums
        for i in xrange(self.process_nums):
            process.append(Process(target=self.worker, args=(i, query_lyric, self.lyric_corpus[i * block_size: min(len(self.lyric_corpus), (i + 1) * block_size)], dis,)))
        for p in process:
            p.start()
        for p in process:
            p.join()
        print dis
        print 'query time: ', time() - start

    def worker(self, i, query, corpus, dis):
        tmp = {}
        for lyric in corpus:
            tmp[lyric['id']] = self.calc_wmd(' '.join(query), ' '.join(lyric['lyrics_jieba']))
        dis[i] = tmp

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    # chinese word2vece model
    w2v_model_path = 'word2vec_models/word2vec_60.bin.gz'
    wmd = WMD(w2v_model_path, 60, 2)
    d1 = u"奥巴马 在 人民 广场 吃 炸鸡"
    d2 = u"在 饭馆 喝 饮料 的 小三"
   
    wmd.query(d1)

