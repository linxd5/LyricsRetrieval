#!/usr/bin/env python
# coding=utf-8

import re, json, jieba, operator, time
from gensim import corpora, models
from scipy import spatial
import numpy as np


"""
doc = 心愿
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
长大间我们是否还会再唱起心愿
"""

doc = """
我还在寻找 一个依靠和一个拥抱
谁替我祈祷 替我烦恼 为我生气为我闹
幸福开始有预兆 缘分让我们慢慢紧靠 
然后孤单被吞没了 
我俩变得有话聊 有变化了
小酒窝常见到 是你最美的记号
我每天睡不着 想念你的微笑
你不知道 你对我多么重要
有了你生命完整的刚好
小酒窝常见到 迷人的无可救药
我放慢了步调 感觉像是盒资料
终于找到心有理智的美好 
一辈子暖暖的好 我永远爱你到老
幸福开始有预兆 缘分让我们慢慢紧靠
"""

# 对文本进行清洗和分词
doc = re.sub(u'[^\u4e00-\u9fa5]', u' ', doc)
doc = jieba.lcut(doc, cut_all=False)

# 载入语料词典
dictionary = corpora.Dictionary.load('/tmp/lyrics.dict')
# 载入语料向量
corpus = corpora.MmCorpus('/tmp/lyrics.mm')

w2v = models.Word2Vec.load('Chinese_Word2Vec/Word60.model')

# 计算语料的 tfidf
tfidf = models.TfidfModel(corpus)

# 取出语料的 wrd2vec
lyrics_vec = []
with open('lyrics_big.json_processed_jieba_tfidf_wrd2vec') as f_read:
    for line in f_read:
        lyrics_vec.append(json.loads(line))
        

begin_time = time.time()

# 对查询歌词建立字典
vec_bow = dictionary.doc2bow(doc)

# 计算查询歌词的向量
doc_vec = np.zeros(60)
for word in tfidf[vec_bow]:
    if dictionary[word[0]] in w2v:
        doc_vec += word[1] * w2v[dictionary[word[0]]]

# 计算相似度并对结果进行排序
lyrics_sim = {}
for item in lyrics_vec:
    lyrics_sim[item['id']] = 1.0-spatial.distance.cosine(doc_vec, item['lyrics_vec'])

sorted_array2 = sorted(lyrics_sim.items(), key=operator.itemgetter(1), reverse=True)

# 返回最相似的 k 个结果
k = 5
print(sorted_array2[:k])

end_time = time.time()

print("+++ Using ", end_time - begin_time, 's')

