#!/usr/bin/env python
# coding=utf-8

import gensim
import json
import numpy as np

# 输入是歌词的 tfidf 文件
# 输出是歌词的向量表示


def wrd2vec(file):
    write_file = file + '_wrd2vec' 
    temp_num = 0
    
    model = gensim.models.Word2Vec.load('Chinese_Word2Vec/Word60.model')

    with open(file) as f_read:
        with open(write_file, 'w') as f_write:
            for line in f_read:
                temp = json.loads(line, "utf-8")
                id, lyrics_tfidf = temp['id'], temp['lyrics_tfidf']

                lyrics_vec, temp_dict = np.zeros(60), {}
                for (key, value) in lyrics_tfidf.items():
                    if key in model:
                        lyrics_vec += lyrics_tfidf[key] * model[key]

                # Numpy array is not JSON serializable 
                # http://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
                temp_dict['id'], temp_dict['lyrics_vec'] = id, lyrics_vec.tolist()
                temp_dict = json.dumps(temp_dict, ensure_ascii=False)
                f_write.write(temp_dict + '\n')

                temp_num += 1
                print('++++ Processing song: ', temp_num)
    return write_file


if __name__ == '__main__':
    file = 'lyrics.json_processed_jieba_tfidf'
    wrd2vec(file)
