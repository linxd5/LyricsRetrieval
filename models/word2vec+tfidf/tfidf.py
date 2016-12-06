#!/usr/bin/env python
# coding=utf-8

# 参考 http://stevenloria.com/finding-important-words-in-a-document-using-tf-idf/


# 输入是分词后的文档（使用空格作为分隔符）
# 输出是每篇文档每个词的 tf-idf 

import math, json
from textblob import TextBlob as tb

def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob.words)

def idf(word, bloblist):
    return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tfidf_word(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)

def tfidf_all(file):
    write_file = file + '_tfidf'
    temp_num, bloblist, temp_id = 0, [], []

    with open(file) as f_read:
        with open(write_file, 'w') as f_write:
            for line in f_read:
                temp = json.loads(line, 'utf-8')
                temp_id.append(temp['id'])
                bloblist.append(tb(' '.join(temp['lyrics_jieba'])))
                temp_num += 1
                print('++++ Concatenating song:', temp_num)

                if temp_num > 10000:
                    break

            for i, blob in enumerate(bloblist):
                print('++++ Processing tfidf:', i)
                temp_dict = {}
                scores = {word: tfidf_word(word, blob, bloblist) for word in blob.words}
                temp_dict['id'], temp_dict['lyrics_tfidf'] = temp_id[i], scores
                temp_dict = json.dumps(temp_dict, ensure_ascii=False)
                f_write.write(temp_dict + '\n')



if __name__ == "__main__":
    file = 'lyrics.json_processed_jieba'
    tfidf_all(file) 

    # 测试代码

    """
    with open('lyrics.json_processed_jieba_tfidf') as file:
        for line in file:
            temp = json.loads(line, 'utf-8')
            print(temp['lyrics_tfidf']['躺'])
    """
