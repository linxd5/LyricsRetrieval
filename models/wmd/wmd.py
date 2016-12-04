#coding=utf8

import os
import sys
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from gensim.models.word2vec import Word2Vec
from sklearn.metrics import euclidean_distances
from pyemd import emd

class WMD:
    def __init__(self, w2v_model_path):
        self.word2vec = Word2Vec.load_word2vec_format(w2v_model_path, binary=True)

    def calc_wmd(self, doc1, doc2):
        vect = CountVectorizer().fit([doc1, doc2])
        vec1, vec2 = vect.transform([doc1, doc2]) 
        vec1 = vec1.toarray().ravel()
        vec2 = vec2.toarray().ravel()

        W = [self.word2vec[w] for w in vect.get_feature_names()]
        D = euclidean_distances(W)
        
        # pyemd needs double precision input
        vec1 = vec1.astype(np.double)
        vec2 = vec2.astype(np.double)
        vec1 /= vec1.sum()
        vec2 /= vec2.sum()
        D = D.astype(np.double)
        D /= D.max()
        return emd(vec1, vec2, D)

if __name__ == '__main__':
    # chinese word2vece model
    w2v_model_path = 'word2vec_models/word2vec_60.bin.gz'
    wmd = WMD(w2v_model_path)
    d1 = "奥巴马 在 人民 广场 吃 炸鸡"
    d2 = "在 饭馆 喝 饮料 的 小三"
    print wmd.calc_wmd(d1, d2)


