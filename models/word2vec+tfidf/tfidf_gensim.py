#!/usr/bin/env python
# coding=utf-8

# 输入是分词后的文档（使用空格作为分隔符）
# 输出是每篇文档的 tf-idf

from gensim import corpora, models
import json

def tfidf_gensim(file):
    temp_num, texts, temp_id = 0, [], []

    with open(file) as f_read:
        for line in f_read:
            temp = json.loads(line, 'utf-8')
            temp_id.append(temp['id'])
            texts.append(temp['lyrics_jieba'])
    
            temp_num += 1
            # if temp_num > 1000:
                # break
    
    # 得到语料库的词典
    dictionary = corpora.Dictionary(texts)
    dictionary.save('processed_data/lyrics.dict')

    # 得到语料库的向量表示
    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize('processed_data/lyrics.mm', corpus)
    
    # 对语料库进行 tfidf 计算
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

    temp_num, write_file = 0, file+'_tfidf'
    with open(write_file, 'w') as f_write:
        for doc in corpus_tfidf:
            temp_dict1, temp_dict2 = {}, {}
            for word in doc:
                temp_dict2[dictionary[word[0]]] = word[1]

            temp_dict1['id'] = temp_id[temp_num]
            temp_dict1['lyrics_tfidf'] = temp_dict2
            temp_dict1 = json.dumps(temp_dict1, ensure_ascii=False)
            f_write.write(temp_dict1 + '\n')

            temp_num += 1
            if temp_num % 10000 == 0:
                print("++++ Processing song:", temp_num)

    return write_file

if __name__ == "__main__":
    file = 'lyrics.json_processed_jieba'
    tfidf_gensim(file)

