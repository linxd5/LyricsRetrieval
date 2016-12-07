#!/usr/bin/env python
# coding=utf-8

import re, json, jieba, time
from gensim import corpora, models
import numpy as np
from sklearn.neighbors import NearestNeighbors


# 输入是查询歌词文档和 k 值
# 输出是最相似的 k 篇歌词文档的 id 

processed_wrd2vec = 'lyrics_all.json_processed_jieba_tfidf_wrd2vec'
processed_data = 'lyrics_all.json_processed'

def query(doc, k):

    # 载入语料词典
    dictionary = corpora.Dictionary.load('/tmp/lyrics.dict')
    # 载入语料向量
    corpus = corpora.MmCorpus('/tmp/lyrics.mm')

    w2v = models.Word2Vec.load('Chinese_Word2Vec/Word60.model')

    # 计算语料的 tfidf
    tfidf = models.TfidfModel(corpus)

    # 取出语料的 wrd2vec
    lyrics_item = []
    with open(processed_wrd2vec) as f_read:
        for line in f_read:
            lyrics_item.append(json.loads(line))

    # 建立 id 到中文歌词的索引
    lyrics_Chinese = {}
    with open(processed_data) as f_read:
        for line in f_read:
            temp = json.loads(line)
            lyrics_Chinese[temp['id']] = temp['lyrics']

    # 对语料的 wrd2vec 建立搜索树 
    lyrics_id, lyrics_vec = [], []
    for item in lyrics_item:
        lyrics_id.append(item['id'])
        lyrics_vec.append(item['lyrics_vec'])
    nbrs = NearestNeighbors(n_neighbors=k, algorithm='brute').fit(lyrics_vec)


    ### 以上部分都是可以预加载的

    begin_time = time.time()

    # 对查询歌词进行清洗和分词
    doc = re.sub(u'[^\u4e00-\u9fa5]', u' ', doc)
    doc = jieba.lcut(doc, cut_all=False)


    # 对查询歌词建立字典
    vec_bow = dictionary.doc2bow(doc)

    # 计算查询歌词的向量
    doc_vec = np.zeros(60)
    for word in tfidf[vec_bow]:
        if dictionary[word[0]] in w2v:
            doc_vec += word[1] * w2v[dictionary[word[0]]]

    # 搜索最相似的 k 首歌词
    distance, indices = nbrs.kneighbors(doc_vec)

    # id 需要映射一下
    result_ids = []
    for index in indices[0]:
        result_ids.append(lyrics_id[index])

    # id 到中文歌词的映射
    result_lyrics = []
    for id in result_ids:
        result_lyrics.append((id, lyrics_Chinese[id]))

    end_time = time.time()
    print("+++ Using ", end_time - begin_time, 's')

    return (distance, result_lyrics)


if __name__ == '__main__':
    doc = """
    [ti:秋天不回来]
    [ar:王强]
    [al:秋天不回来]
    [by:晨曦之光]
    歌曲名:秋天不回来
    专辑:秋天不回来
    演唱:王强
    ☆音乐☆.初秋的天冰冷的夜
    回忆慢慢袭来
    真心的爱就像落叶
    为何却要分开
    灰色的天独自彷徨
    城市的老地方
    真的孤单走过忧伤
    心碎还要逞强
    想为你披件外衣
    天凉要爱惜自己
    没有人比我更疼你
    告诉你在每个
    想你的夜里
    我哭的好无力
    就让秋风带走我的思念
    带走我的泪
    我还一直静静守候在
    相约的地点
    求求老天淋湿我的双眼
    冰冻我的心
    让我不再苦苦奢求你还
    回来我身边我身边～
    """

    distance, lyrics = query(doc, 20)

    for lyric in lyrics:
        print(lyric[0], ' +++++ ', lyric[1], '\n\n')
