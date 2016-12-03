大作业项目是**使用歌词搜索歌词**。

采用的技术有：
- word2vec+TFIDF，使用Word2Vec得到词语的表示，然后使用TFIDF作为词语的权重组合得到歌词文档的向量表示。
- WMD，来自这篇论文[From word Embeddings To Document Distances](jmlr.org/proceedings/papers/v37/kusnerb15.pdf)

相关的文件：

- Chinese_Word2Vec：来自 http://www.cnblogs.com/Darwin2000/p/5786984.html。 使用中文维基百科训练出来的词向量。文件地址：/data/lindayong/Chinese_Word2Vec