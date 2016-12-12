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
        self.process_nums = process_nums

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

    def query(self, query_lyric, corpus):
        start = time()
        manager = Manager()
        dis = manager.dict()

        process = []
        block_size = len(corpus) / self.process_nums
        corpus_list = []
        for i in xrange(self.process_nums):
            corpus_list.append(corpus[i * block_size: (i + 1) * block_size])
        corpus_list[-1].extend(corpus[self.process_nums * block_size: len(corpus)])

        for i in xrange(self.process_nums):
            process.append(Process(target=self.worker, args=(i, query_lyric, corpus_list[i], dis,)))
        for p in process:
            p.start()
        for p in process:
            p.join()
        ans = []
        for index in dis.keys():
            for key in dis[index].keys():
                ans.append((key, dis[index][key]))
        ans = sorted(ans, key=lambda x: x[1])
        print dis
        print ans
        print 'query time: ', time() - start
        return ans

    def worker(self, i, query, corpus, dis):
        print corpus
        tmp = {}
        for lyric in corpus:
            tmp[lyric[0]] = self.calc_wmd(' '.join(query), ' '.join(lyric[1]))
        print tmp
        dis[i] = tmp

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    # chinese word2vece model
    w2v_model_path = 'word2vec_models/word2vec_60.bin.gz'
    wmd = WMD(w2v_model_path, 60, 3)
    d1 = [" ", "如何", "不可思议", "的", "解释", " ", "总", "找到", "借口", "补救", " ", "如何", "不可", "解决", "的", "纷争", " ", "总", "可以", "迁就", " ", "完全", "不", "懂", "保留地", "接受", " ", "贪恋", "抱", "着", "你", "在", "我", "的", "手", " ", "只", "因", "你", "让", "我", " ", "有过", "最", "快乐", "时候", " ", "如", "情感", "早早", "变质", " ", "简单", "讲", "一句", "已经", "足够", " ", "然而", "今天", "当", "你", "要", "飞", "走", " ", "解释", "太", "荒谬", " ", "平平静静", "地", "从没", "分手", " ", "不可", "证实", "这份", "爱算否", "足够", " ", "还是", "冷静", "过", " ", "抉择", "过", "以后", "再", "走", " ", "其实", "若", "你", "想", "这里", "放手", " ", "不要", "对", "我", "说", "以后", " ", "无谓", "随便", "乱说", "错误引导", " ", "使", "我", "有", "复合", "念头", " ", "无论是", "你", "编", "哪个", "借口", " ", "不会", "再教", "我", "接受", " ", "其实", "是", "你", "玩够", "厌倦", "了", " ", "今天", "要", "走", " ", "你", "爱", "我", "不", "足够", " ", "如何", "不可思议", "的", "解释", " ", "总", "找到", "借口", "补救", " ", "如何", "不可", "解决", "的", "纷争", " ", "总", "可以", "迁就", " ", "完全", "不", "懂", "保留地", "接受", " ", "贪恋", "抱", "着", "你", "在", "我", "的", "手", " ", "只", "因", "你", "让", "我", " ", "有过", "最", "快乐", "时候", " ", "如", "情感", "早早", "变质", " ", "简单", "讲", "一句", "已经", "足够", " ", "然而", "今天", "当", "你", "要", "飞", "走", " ", "解释", "太", "荒谬", " ", "平平静静", "地", "从没", "分手", " ", "不可", "证实", "这份", "爱算否", "足够", " ", "还是", "冷静", "过", " ", "抉择", "过", "以后", "再", "走", " ", "其实", "若", "你", "想", "这里", "放手", " ", "不要", "对", "我", "说", "以后", " ", "无谓", "随便", "乱说", "错误引导", " ", "使", "我", "有", "复合", "念头", " ", "无论是", "你", "编", "哪个", "借口", " ", "不会", "再教", "我", "接受", " ", "其实", "是", "你", "玩够", "厌倦", "了", " ", "今天", "要", "走", " ", "你", "爱", "我", "不", "足够", " ", "其实", "若", "你", "想", "这里", "放手", " ", "不要", "对", "我", "说", "以后", " ", "无谓", "随便", "乱说", "错误引导", " ", "使", "我", "有", "复合", "念头", " ", "无论是", "你", "编", "哪个", "借口", " ", "不会", "再教", "我", "接受", " ", "其实", "是", "你", "玩够", "厌倦", "了", " ", "今天", "要", "走", " ", "你", "爱", "我", "不", "足够", " ", "你", "对", "我", "的", "爱", "不", "足够", " ", "情牵", " "]
    #d1 = [u"奥巴马", u"在", u"人民", u"广场", u"吃" u"炸鸡"]
    d2 = u"在 饭馆 喝 饮料 的 小三"
    lyric_corpus = []
    with open('lyrics_100.txt', 'r') as f:
        for line in f.readlines():
            lyric = json.loads(line.strip())
            lyric_corpus.append((lyric['id'], lyric['lyrics_jieba']))
    wmd.query(d1, lyric_corpus)
