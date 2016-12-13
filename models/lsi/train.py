#coding: utf-8

import cPickle
import time
import json
import jieba
#import pprint
import re
from collections import defaultdict

from gensim import corpora, models, similarities
from six import iteritems

jieba.initialize()

def timing_val(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        return (t2 - t1), res, func.__name__
    return wrapper


def json2pair(filename = './data/lyrics_all.json', ifpair = False, verbose = True):
    # read json from file, and return lyric strings
    pair_count, total_count = 0, 0
    for jsonstr in open(filename):
        dict_lyrics = json.loads(jsonstr)
        if dict_lyrics['lyrics'] != '':
            pair_count = pair_count + 1
            pair = (int(dict_lyrics['id']), dict_lyrics['lyrics'])
            if ifpair:
                yield pair
            else:
                yield dict_lyrics['lyrics']
        total_count = total_count + 1
        if total_count % 10000 == 0 and verbose == True:
            print("total count: %d, pair count = %d" %(total_count, pair_count))

def dump_lyrics():
    lyrics_hash = defaultdict(str) # default value is ''
    for songid, lyric in json2pair(ifpair=True):
        lyrics_hash[songid] = lyric
    data_string = cPickle.dumps(lyrics_hash)
    # remove things like [00:01:20]
    data_string = re.sub(r'\[\d\d:\d\d[\.:]\d\d\]', '', data_string)
    print('dumping lyrics.hash')
    with open('lyrics.hash', 'wb') as f:
        f.write(data_string)
        f.close()


def dump_song_detail():
    song_detail = defaultdict(str)
    song_detail_path = "/data/zhangxb/db_project/dataset/wymusic/lyrics/songs_detail.json"
    for detail in open(song_detail_path, 'r'):
        temp = json.loads(detail)['data']['songs']
        if len(temp) == 0:
            print(detail)
            continue
        else:
            detail = temp[0]
        #pprint.pprint(detail)
        #print(detail['songid'])
        songid = detail['id']
        single_song_detail = {}
        single_song_detail['popularity'] = detail['popularity']
        single_song_detail['name'] = detail['name']
        single_song_detail['picUrl'] = detail['album']['blurPicUrl']
        single_song_detail['artists'] = [artist['name'] for artist in detail['artists']]
        song_detail[str(songid)] = single_song_detail
    print('saving song detail')
    with open('song_detail.pickle', 'wb') as f:
        cPickle.dump(song_detail, f)
        f.close()

def lyric2text(lyric):
    # lyric string of one song -> token list
    lyric = re.sub(r'\[\d\d:\d\d[\.:]\d\d\]', '', lyric) # remove things like [00:01:20]
    lyric = re.sub(r'[\n\r \t]{1,}', ' ', lyric) # remove \n \r
    text = jieba.lcut(lyric, cut_all=True) # jieba cut, will return a list
    text = filter(lambda s: s.strip() != '', text) # filter '', '\n', etc
    text = map(lambda s: s.strip(), text)     # strip for token like ' abc '
    return text

def get_texts():
    # this function is both time-consuming and memory-consuming
    songids, texts = [], []
    for songid, lyric in json2pair(ifpair = True):
        text = lyric2text(lyric)
        texts.append(text)
        songids.append(songid)
    print('get %d lyrics' %(len(texts)))

    return songids, texts


def get_dictionary(texts):
    dictionary = corpora.Dictionary(texts)
    once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]
    dictionary.filter_tokens(once_ids)
    dictionary.compactify()

    return dictionary

def get_corpus(dictionary, texts):
    corpus = []
    for i, text in enumerate(texts):
        c = dictionary.doc2bow(text)
        corpus.append(c)
        if i % 10000 == 0:
            print(i)

    return corpus

def fit_tfidf(corpus):
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    return tfidf, corpus_tfidf


def fit_lsi(dictionary, corpus_tfidf):
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics = 300) # 200~500
    corpus_lsi = lsi[corpus_tfidf]
    return lsi, corpus_lsi


def pipline():
    """
    this function may cost almost 2 hours for lyrics_all.json
    """
    songids, texts = get_texts()
    dictionary = get_dictionary(texts)
    corpus = get_corpus(dictionary, texts)

    # fitting models
    tfidf, corpus_tfidf = fit_tfidf(corpus)
    lsi, corpus_lsi = fit_lsi(dictionary, corpus_tfidf)

    # fiting similarity matrix
    index = similarities.MatrixSimilarity(corpus_lsi)

    print('saving songids')
    with open('songids.pickle', 'wb') as f:
        cPickle.dump(songids, f)
        f.close()

    print('saving corpus.mm')
    corpora.MmCorpus.serialize('corpus.mm', corpus)

    print('saving lyric.dict')
    dictionary.save('lyrics.dict')

    print('saving corpus_lsi.mm')
    corpora.MmCorpus.serialize('corpus_lsi.mm', corpus_lsi)

    print('saving lyrics.lsi')
    lsi.save('lyrics.lsi')

    print('saving lyrics.index')
    index.save('lyrics.index')

if __name__ == '__main__':
    #pipline()
    dump_lyrics()
    #dump_song_detail()
