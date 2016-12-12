# encoding=utf8
from gensim import corpora, models, similarities
from train import lyric2text
import cPickle

def load_model():
    print('loading dictionary')
    dictionary = corpora.Dictionary.load('lyrics.dict')

    print('loading lsi')
    lsi = models.LsiModel.load('lyrics.lsi')

    print('loading corpus_lsi')
    corpus_lsi = corpora.MmCorpus('corpus_lsi.mm')

    print('loading index')
    index = similarities.MatrixSimilarity.load('lyrics.index')

    print('done loading models')

    return dictionary, lsi, corpus_lsi, index


def test_query(dictionary, lsi):
    doc = ""
    with open('./data/query_example.txt', 'r') as f:
        doc = ''.join(f.readlines()).strip()
        print doc
        f.close() # ??
        print('len of doc = %d, type of doc is %s' %(len(doc), type(doc)) )
    doc_cut = lyric2text(doc)
    vec_bow = dictionary.doc2bow(doc_cut)
    vec_lsi = lsi[vec_bow]

    return vec_lsi


def fit_similarity(corpus_lsi, vec_lsi, index):
    sims = index[vec_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])

    print('sims', type(sims))
    print(sims[0:3])

    return sims

#@profile
def pipline():
    songids = cPickle.load(open('songids.pickle', 'rb'))
    dictionary, lsi, corpus_lsi, index = load_model()
    vec_lsi = test_query(dictionary, lsi)
    sims = fit_similarity(corpus_lsi, vec_lsi, index)

    for i in range(10):
        idindex, score = sims[i]
        print 'songid = %d, score = %f' %(songids[idindex], score)

if __name__ == '__main__':
    pipline()
