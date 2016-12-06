#!/usr/bin/env python
# coding=utf-8

import gensim
import json
import numpy as np

def wrd2vec(file):
    write_file = file + '_wrd2vec' 
    
    model = gensim.models.Word2Vec.load('Chinese_Word2Vec/Word60.model')

    with open(file) as f_read:
        with open(write_file, 'w') as f_write:
            for line in f_read:
                temp = json.loads(line, 'utf-8')
                id, lyrics_tfidf = temp['id'], temp['lyrics_tfidf']
                lyrics_vec, temp_dict = np.zeros(60), {}
                for (key, value) in lyrics_tfidf.items():
                    if key in model:
                        lyrics_vec += lyrics_tfidf[key] * model[key]

                temp_dict['id'], temp_dict['lyrics_vec'] = id, lyrics_vec
                temp_dict = json.dumps(temp_dict, ensure_ascii=False)
                f_write.write(temp_dict + '\n')

if __name__ == '__main__':
    file = 'lyrics.json_processed_jieba_tfidf_small'
    wrd2vec(file)
