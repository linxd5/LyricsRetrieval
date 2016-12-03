#!/usr/bin/env python
# coding=utf-8

# 参考 http://stevenloria.com/finding-important-words-in-a-document-using-tf-idf/


# 输入是分词后的文档（使用空格作为分隔符）
# 输出是每篇文档每个词的 tf-idf 

import math
from textblob import TextBlob as tb

def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob.words)

def idf(word, bloblist):
    return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)

document1 = tb("""我 来到 北京 清华大学""")

document2 = tb("""他 来到 了 网易 杭研 大厦""")

document3 = tb("""小明 硕士 毕业 与 中国 科学院""")

document4 = tb("""我 爱 北京 天安门""")

bloblist = [document1, document2, document3, document4]
for i, blob in enumerate(bloblist):
    print("Top words in document {}".format(i + 1))
    scores = {word: tfidf(word, blob, bloblist) for word in blob.words}
    for (word, score) in scores.items():
        print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))

