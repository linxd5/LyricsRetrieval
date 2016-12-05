### 1. 模型训练过程

- 对网易云音乐的数据进行清洗，去除掉与歌词无关的东西。
- 对处理好后的数据进行 jieba 分词，保存分词后的歌词。
- 使用分词后的歌词，统计 TF-IDF。(`tf-idf.py`)
- 对于每一首歌，得到每一个分词的词向量。组合该分词的 TF-IDF，得到整篇歌词的向量表示。


### 2. 模型预测过程

- 从前端的文本框中获取歌词
- 计算查询歌词的 TF-IDF，组合得到查询歌词的向量表示。
- 与库中的每一首歌做相似度对比，得到推荐歌词。
- 向前端返回推荐歌词。


### 3. 进度报告

#### 2016年12月5日
- 将 tf-idf 改造成可供调用的函数
- 配置[虚拟环境](http://docs.python-guide.org/en/latest/dev/virtualenvs/)，通过子目录下的 `.gitignore` 将虚拟环境文件设置为[不上传](http://blog.csdn.net/nyist327/article/details/39207383)。

#### 2016 年12月3日
参考 http://stevenloria.com/finding-important-words-in-a-document-using-tf-idf/，实现了能运行的 tf-idf。

