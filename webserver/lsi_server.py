#!/usr/bin/env python
# coding=utf-8

import os.path

from flask import Flask, request, render_template, jsonify
from gensim import corpora, models, similarities
app = Flask(__name__)
import sys
import cPickle
import time
sys.path.append('../')
from models.lsi.train import lyric2text

# loading lsi models
print('loading models')
begin = time.time()
lsi_root_dir = '/data/zhangxb/db_project/models/lsi/persistence/'
lsi_dict = corpora.Dictionary.load(os.path.join(lsi_root_dir, 'lyrics.dict'))
lsi = models.LsiModel.load(os.path.join(lsi_root_dir, 'lyrics.lsi'))
lsi_corpus= corpora.MmCorpus(os.path.join(lsi_root_dir, 'corpus_lsi.mm'))
lsi_index = similarities.MatrixSimilarity.load(os.path.join(lsi_root_dir, 'lyrics.index'))
lsi_songids = cPickle.load(open(os.path.join(lsi_root_dir, 'songids.pickle'), 'rb'))
lyrics_hash = cPickle.load(open(os.path.join(lsi_root_dir, 'lyrics.hash'), 'rb'))
song_detail = cPickle.load(open(os.path.join(lsi_root_dir, 'song_detail.pickle'), 'rb'))
end = time.time()
print('done loading models, cost %f seconds' %(end - begin))

@app.route('/query', methods=['POST'])
def query():
    #print(request.form)
    k_input = int(request.form.get('k_input', '1'))
    query_lyric = request.form.get('query_lyric', '')
    pop_input = float(request.form.get('pop_input', '1.0'))
    #model = request.form.get('model', '')

    #if model == 'lsi':
    doc_cut = lyric2text(query_lyric)
    vec_bow = lsi_dict.doc2bow(doc_cut)
    vec_lsi = lsi[vec_bow]
    sims = lsi_index[vec_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    songids = [lsi_songids[idindex] for idindex, score in sims[0:k_input]]
    sim_lyrics = [(str(songid), lyrics_hash[songid]) for songid in songids]
    songs_info = [song_detail[songid] for songid in songids]

    # re-order according to popularity weight
    weight = [(sims[i][1] + pop_input / 100 * songs_info[i]['popularity']) for i in range(k_input)]
    weight = sorted(enumerate(weight), key = lambda x: x[1] , reverse=True) # [(index, new_weight), (), ()]

    # re-order sim_lyrics and songs_info according to new weight
    sim_lyrics = [sim_lyrics[weight[i][0]] for i, sim in enumerate(sim_lyrics)]
    songs_info = [songs_info[weight[i][0]] for i, info in enumerate(songs_info)]

    return jsonify(sim_lyrics=sim_lyrics, songs_info=songs_info)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='172.18.217.250', port=9991)
