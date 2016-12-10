#!/usr/bin/env python
# coding=utf-8

from flask import Flask, request, render_template, jsonify
app = Flask(__name__)


import re, json, jieba
from gensim import corpora, models
import numpy as np
from sklearn.neighbors import NearestNeighbors

import operator



# 输入是查询歌词文档和 k_input 值
# 输出是最相似的 k_input 篇歌词文档的 id 


### 模型预加载

processed_wrd2vec = '../processed_data/lyrics_all.json_processed_jieba_tfidf_wrd2vec'
processed_data = '../processed_data/lyrics_all.json_processed'
corpus_data = '../processed_data/lyrics.mm'
dictionary_data = '../processed_data/lyrics.dict'
Chinese_Word2Vec_data = '../Chinese_Word2Vec/Word60.model'
Chinese_songs_detail = '../processed_data/Chinese_songs_detail.json'

# 预建立 k_max 的搜索树，根据用户输入再返回 k_input(< k_max) 篇相似文档
k_max, k_input = 260000, 5

# 对于 popularity 信息缺失的歌曲，采用默认的 popularity 值 
pop_default, pop_input = 20, 0

# 载入语料词典
dictionary = corpora.Dictionary.load(dictionary_data)
# 载入语料向量
corpus = corpora.MmCorpus(corpus_data)

w2v = models.Word2Vec.load(Chinese_Word2Vec_data)

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

# 建立 id 到歌曲详细信息的索引
songs_detail_Chinese = {}
for line in open(Chinese_songs_detail):
    temp = json.loads(line)
    songs_detail_Chinese[temp['id']] = temp['song_detail']


# 对语料的 wrd2vec 建立搜索树 
lyrics_id, lyrics_vec = [], []
for item in lyrics_item:
    lyrics_id.append(item['id'])
    lyrics_vec.append(item['lyrics_vec'])
nbrs = NearestNeighbors(n_neighbors=k_max, algorithm='brute').fit(lyrics_vec)
###nbrs = NearestNeighbors(n_neighbors=k_max, algorithm='auto').fit(lyrics_vec)

@app.route('/query', methods=['POST'])
def query():

    k_input = int(request.form.get('k_input', ''))
    query_lyric = request.form.get('query_lyric', '')
    pop_input = request.form.get('pop_input', '')

    # 对查询歌词进行清洗和分词
    query_lyric = re.sub(u'[^\u4e00-\u9fa5]', u' ', query_lyric)
    query_lyric = jieba.lcut(query_lyric, cut_all=False)


    # 对查询歌词建立字典
    query_lyric_dict = dictionary.doc2bow(query_lyric)

    # 计算查询歌词的向量
    query_lyric_vec = np.zeros(60)
    for word in tfidf[query_lyric_dict]:
        if dictionary[word[0]] in w2v:
            query_lyric_vec += word[1] * w2v[dictionary[word[0]]]

    # 搜索最相似的 k_max 首歌词
    distance, indices = nbrs.kneighbors(query_lyric_vec)


    # 综合考虑歌词的匹配度和歌曲的流行度 
    dis_pop = {}
    for i in range(len(indices[0])):
        # id 需要使用 lyrics_id 映射一下
        id = str(lyrics_id[indices[0][i]])
        popularity = pop_default
        if id in songs_detail_Chinese and 'popularity' in songs_detail_Chinese[id]:
            popularity = songs_detail_Chinese[id]['popularity']
        dis_pop[id] = distance[0][i] - float(pop_input) * popularity
    sorted_dis_pop = sorted(dis_pop.items(), key=operator.itemgetter(1))
    

    # 只返回最相似的 k_input 个 id
    result_ids = [sorted_dis_pop[i][0] for i in range(k_input)]
    #for i in range(k_input):
        # result_ids.append(sorted_dis_pop[i][0])

    # id 到中文歌词的映射
    sim_lyrics = [(id, lyrics_Chinese[id]) for id in result_ids]
    # for id in result_ids:
        # sim_lyrics.append((id, lyrics_Chinese[id]))

    # 通过 songs_detail_Chinese 得到歌曲相关信息
    songs_info = [songs_detail_Chinese[songid] for songid in result_ids]

    return jsonify(sim_lyrics=sim_lyrics, songs_info=songs_info)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=2333)
