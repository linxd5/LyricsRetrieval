[toc]


## 0. 运行环境

- Ubuntu 14.04

- python3 ~~ (ln -s /usr/bin/python3.4 /usr/bin/python，会导致 Ubuntu 14.04 系统安装软件异常)~~  `virtualenv -p /usr/bin/python3.4 venv `

- sudo apt-get install subversion

- pip install jieba numpy gensim flask sklearn (建议一个一个顺序安装)

- 与项目相关的数据文件放在的[百度云盘](https://pan.baidu.com/s/1hsgEc08)。

- 在海外服务器上部署时，还需要 sudo apt-get update && sudo apt-get dist-upgrade。海外服务器只有 500m 的内存，不支持训练和部署。。。。

### 0.1 如何运行代码

通过 git pull 得到最新的代码，进入 python3 虚拟环境：

- `python train.py` 将在原数据文件目录下依次产生清洗后的数据文件 *_processed、jieba 分词文件 *_processed_jieba、统计 TF-IDF 文件 *_processed_jieba_tfidf、词向量文件 *_processed_jieba_tfidf_wrd2vec。以及语料词典 lyrics.dict 、语料向量 lyrics.mm 以及 lyrics.mm.index 文件。运行程序前记得把之前生成的文件删除，否则会出现一些奇怪的错误。内存要求：6G+

- 进行 web 目录下，运行 `python server.py`，待模型加载完后，就可以接受用户的歌词查询了。内存要求：2G+


tian 程序常驻后台，通过 172.18.217.250:2333 即可访问网站

后台运行程序：`setsid python server.py 2>&1 ~/db_project.log`

关闭后台程序：`ps -aux | grep server.py`，找到进程 ID 并 kill -9 。

- 访问网站的时候请清除该网站的缓存，否则网站会优先加载已缓存的文件。这会导致一些更新效果没有办法显示出来。


## 1. 模型训练过程

- 对网易云音乐的数据进行清洗，去除掉与歌词无关的东西。这里使用正则表达式把非中文歌词替换为空格。数据的读取和写出使用 python json 函数，读入时以 utf-8 编码读入，写出时转换为中文编码。以下步骤的文件读写是类似的，就不再赘述了。 (`preprocess_json.py`)

- 对处理好后的数据进行 jieba 分词（精确模式），保存分词后的歌词 (`jieba_seg.py`)。

- 使用分词后的歌词，统计 TF-IDF。这里使用了  gensim 的库来对语料建立词典和向量，保存相应的文件以备查询时用。同时使用库计算了  TF-IDF。 (`tf-idf.py`)

- 对于每一首歌，得到每一个分词的词向量。组合该分词的 TF-IDF，得到整篇歌词的向量表示(`wrt2vec.py`)。

### 1.1 结巴分词深入理解

关于结巴分词的理解可以参考 [系列文档一](http://www.cnblogs.com/zhbzz2007/p/6076246.html)、[系列文档二](http://www.cnblogs.com/baiboy/p/jieba1.html)。

结巴分词使用了`前缀词典`来预加载语料词典，里面有每个词语以及它们出现的频数。对于待分词的句子，根据前缀词典生成所有可能成词情况所构成的`有向无环图`。有向无环图中有很多条分词路径，采用`动态规划`来查找基于词频的最大概率路径。对于未登录词，采用基于汉字成词能力的 `HMM 模型`，使用了 Viterbi 算法。

结巴分词的核心代码只有大概 1000 行，如果有时间的话一定要拜读一下！！！


### 1.2 gensim TF-IDF 深入理解

使用 [A guide to analyzing Python performance](https://www.huyng.com/posts/python-performance-analysis) 来测量如下代码的内存占用：
```python 
#!/usr/bin/env python
# coding=utf-8

# 输入是分词后的文档（使用空格作为分隔符）
# 输出是每篇文档的 tf-idf

from gensim import corpora, models
import json, time


@profile
def run(file):
    temp_num, texts, temp_id = 0, [], []

    with open(file) as f_read:
        for line in f_read:
            temp = json.loads(line, 'utf-8')
            temp_id.append(temp['id'])
            texts.append(temp['lyrics_jieba'])
    
            temp_num += 1
        
if __name__ == '__main__':
    file = 'processed_data/lyrics_all.json_processed_jieba'
    run(file)
```

发现读取文件占用了 4G 的内容，同时接下来的代码：
```python
 # 得到语料库的词典
dictionary = corpora.Dictionary(texts)
```
并不支持增量字典迭代，texts 必须是全语料的文本，所以最终放弃内存占用的优化！！


对于 raw_text 的语料文本：

- 通过 dictionary = corpora.Dictionary 把语料中的每个词映射成唯一的数字 ID（通过 dictionary.token2ed 访问） ，同时统计每个词在语料中出现的次数（IDF，通过 dictionary.dfs 访问）。

- 然后通过 corpus = dictionary.doc2bow 对语料进行数字化，即文档中的每个词（ID）在该文档中出现了多少次，这也相当于统计每篇文档的词频（TF）。

- 最后调用 models.TfidfModle(corpus) 就可以将文档中每个词出现的次数快速地转换成 TF-IDF 。 


### 1.3 深入理解 word2vec 


## 2. 模型预测过程

- 从前端的文本框中获取歌词，涉及到 $.ajax 以及数据的序列化 (serialize)，详见 /web/static/index.js

- 计算查询歌词的 TF-IDF，组合得到查询歌词的向量表示，然后与库中的每一首歌词向量做相似度对比，得到推荐歌词，并前端返回推荐歌词。这里把预加载模型写在外部代码中，这样就不用每来一个查询都要加载模型。然后把查询代码写在路由 /query 中，并使用 python.jsonify 向前端返回结果。这里计算相似度的时候使用了 sklearn.neighbors.NearestNeighbors 函数，参数算法采用 'brute'，这是实测的跑得最快又准确的参数算法。详见 /web/server.py

### 2.1 深入理解 NearestNeighbors

[官方文档](http://scikit-learn.org/stable/modules/neighbors.html#brute-force)里面说 Brute Force 是最 Naive 的实现，它对所有样本点两两之间计算相似度。但是不知道为什么，在我的测试中，这个方法是最快的？？

下面的训练时间是指 NearestNeighbors().fit() 这行代码运行的时间，预测时间是指从得到查询歌词到返回相似歌词结果的时间。前面的数值是训练时间，后一个数值是预测时间。

- brute，0.4s / 0.9s
- kd_tree，1.7s / 1s
- ball_tree，1.9s / 0.9s
- auto，0.4s / 0.9s

训练时间相差比较大，预测时间几乎相同。


## 3. 进度报告


### 加入歌曲信息

- 因为小彬师兄在爬着网易云音乐的歌曲信息，导致我在请求歌曲信息的时候极容易 timeout !!

- 预处理小彬师兄爬下来的网易云音乐的歌曲信息，只保留中歌曲的歌名、歌手、图片和流行度，代码在 backup_data 下的 preprocess_songs_detail.ipynb

- 基本处理完 popularity 的逻辑； 需要注意的是，搜索流行歌曲的时候，加大 pop_input 可以筛选掉一些翻唱的版本。但是搜索不热门歌曲，例如校歌和儿歌的时候，pop_input 建议设置为 0。 

- 增加了[音乐 icon](http://www.iconfont.cn/plus/search/index?searchType=icon&q=%E9%9F%B3%E7%AC%A6&page=1)，增加了歌曲之间的[分割线](https://codepen.io/ibrahimjabbari/pen/ozinB)



### 2016年12月9日

- 优化了 CSS 代码，k_input 框增加回车搜索功能。

- 深入理解结巴分词、gensim TF-IDF

- 依照产品经理小彬师兄的要求，在返回的数据中加入了歌名、歌手以及图片。同时增加 popularity 特征来对歌曲进行排序。这里 popularity 的数值在 0-100 之间，distance 的数值，如果 k_max 设置为 50000 的话，在 0-20 之间； 如果 k_max 设置为 26000 的话，在 0-58 之间；

### 测试报告

- 热门的歌曲返回的大多都是同一首歌，这时候需要加大 k_input，才能看到其它歌曲。

- 搜索中山大学校歌歌词，可以得到其它学校的校歌歌词。

- 搜索某一首儿歌的话，可以发现返回的几乎也是儿歌。

- 接下来是对整个项目进行深入的总结和整理，同时做 ppt 。

### flask 专题 (Demo 模板)

- 把任务划分成独立的子任务 (清洗，分词，TF-IDF，词向量)。把测试划分成尽可能小、完备、快速 (ipython notebook) 的测试 (正则，flask外部访问)！！！

- 修改 app.run() 为 app.run(host='0.0.0.0', port=2333)，可以实现从外部访问网站，端口设置为附加功能。这里要注意关掉浏览器代理！！

- 访问网站 / 的时候，会返回 index.html；在 index.html 上点击按钮时，会向 /query 发送查询歌词数据；后台在处理完后向前端返回相似歌词数据 (jsonify)；前端得到数据后进行相应的更新。[使用 jsonify 的好处](http://stackoverflow.com/questions/7907596/json-dumps-vs-flask-jsonify)是它会自动在响应中加入头部。

### 2016年12月7日

- 详细的更新了本文档，优化了前端代码，并把项目部署到 titan 中，实现外网访问。

- 网站也基本搭好了，剩下就是布局和样式了！

- 今天早上调用了 sklearn.neighbors.NearestNeighbors，成功把查询时间从原来的 11s 下降到 0.2s，amazing!!

- 查询时间主要花在相似度的计算上，接下来的重点是如何高效地计算相似度！

### 2016年12月6日

如何高效地得到最相似的 K 首歌？ 

- gensim.MatrixSimilarity 好是好，但我的数据不知道怎么放进去。
- sklearn.neighbors.NearestNeighbors 好像不符合我的需求？
- 目前使用的是 spatial.distance.cosine 计算两个向量的相似度，然后进行排序并返回前 k 个结果。


- preprocess_json.py 是使用 json 对数据进行清洗的程序； preprocess_re.py 是使用正则表达式对数据进行清洗的程序；

- 使用 gensim tfidf 能够高效地统计 TF-IDF (`tfidf_gensim.py`)。 gensim tfidf 的文档，教你如何使用 LSA 来得到两篇文档的相似度并返回最相似的 k 篇文档：
	- [Corpora and Vector Spaces](https://radimrehurek.com/gensim/tut1.html)
	- [Topics and Transformations](https://radimrehurek.com/gensim/tut2.html)
	- [Similarity interface](https://radimrehurek.com/gensim/tut3.html)

gensim tfidf 还有很多高级的内容，有需要的话再去看把！

目前基本的功能已经实现完成，包括对数据进行清洗，jieba 分词，统计 TF-IDF，得到每首歌的词向量。

接下来要做的事情是：

- 如何高效地得到最相似的 K 首歌？
- 前端的工作

### 字符串编码专题

python json.loads() 和 json.dumps() 函数是正常执行的。但是中间的正则匹配除了问题，初步怀疑是 json.loads() 装载数据时字符串编码出了问题。

json.[loads](https://docs.python.org/2/library/json.html)(s, [encoding]) 官方文档里面提到：

> If s is a str instance and is encoded with an ASCII based encoding other than UTF-8 (e.g. latin-1), then an appropriate encoding name must be specified. Encodings that are not ASCII based (such as UCS-2) are not allowed and should be decoded to unicode first.


于是尝试判断一下装载进来的 lyrics 是什么[编码格式](http://stackoverflow.com/questions/4987327/how-do-i-check-if-a-string-is-unicode-or-ascii)？

```python
def whatisthis(s):
    if isinstance(s, str):
        print "ordinary string"
    elif isinstance(s, unicode):
        print "unicode string"
    else:
        print "not a string"
```

输出的结果显示 lyrics 是 ordinary string。因此在 json.loads 里面加入 'utf-8' encoding，完美解决！

python str 和 unicode 的[最佳实践](http://blog.ernest.me/post/python-setdefaultencoding-unicode-bytes)：

- 使用 python3。python2 默认的编码方式是 ASCII，因此会存在编解码的问题； python3 默认的编码方式是 Unicode，不存在编解码的问题。

- 所有 text string 都应该是 unicode 类型，而不是 str，如果你在操作 text，而类型却是 str，那就是在制造 bug。


[让 python 的 json.dumps 输出中文](http://outofmemory.cn/code-snippet/4092/python-json-charset-type)：

python 的 json.dumps 方法默认会输出成这种格式 `"\u535a\u5ba2\u56ed"`。要输出中文需要指定 ensure_ascii 参数为 False，如下代码片段：
```python
json.dumps({'text': "中文"}, ensure_ascii=False)
```

需要注意的是，每次向文件中写入一首处理好的歌词的时候，要在末尾加上空格，以方便后面的处理，代码如下：
```python
temp_dict = json.dumps(temp_dict, ensure_ascii=False)
f_write.write(temp_dict + '\n')
```




### 数据清洗专题报告

需要明确的一点是：`中文和英文没有相似的概念`，因为训练文本极少是中英文混合的。具体的代码如下：
```python
>>> import gensim
>>> model = gensim.models.Word2Vec.load('Chinese_Word2Vec/Word60.model')
>>> model.most_similar('hello')
[('Any', 0.8719050884246826), ('move', 0.867795467376709), ('next', 0.8668863773345947), ('note', 0.8605353832244873), ('join', 0.8506414890289307), ('word', 0.8469972610473633), ('bad', 0.8433617949485779), ('case', 0.8418437242507935), ('argument', 0.841327428817749), ('anonymous', 0.8405176997184753)]
>>> model.most_similar('你好')
[('哦', 0.8678715229034424), ('您好', 0.8638617992401123), ('生日快乐', 0.8592998385429382), ('对不起', 0.8480029106140137), ('哟', 0.8415143489837646), ('喔', 0.8251286745071411), ('说声', 0.8165164589881897), ('非常感谢', 0.8138009309768677), ('嗨', 0.808462381362915), ('呀', 0.8067286014556885)]
```
从上面的代码可以看出，中文的最相似词只有中文，英文的最相似词只有英文。如果后面要做中英文歌曲的互相搜索的话，需要先翻译成同一种语言。

所以在做数据清洗的时候，我们需要做的事情如下：

- 抽取出歌词字段。
- 去除无关歌词的信息。

这里比较关键的是`如何去除无关歌词的信息？`

最开始的做法是分别写正则表达式去除歌曲中的时间戳，以及去除英文歌。去除英文歌时先对歌曲进行空格切分，然后检查里面是否包含[a-zA-Z]，包含的个数达到一定上限时，就认为这首歌是英文歌。这个做法有如下不好的地方：

- 上限值需要手动设置
- 除了英文歌，不一定就是中文歌。还有韩文歌，日文歌之类的。

后面的做法很简单粗暴：`直接把歌曲中不是[中文的字符](https://www.zhukun.net/archives/6397)置换为空格`，然后效果奇好。


### 2016年12月5日
- 将 tf-idf 改造成可供调用的函数
- 配置[虚拟环境](http://docs.python-guide.org/en/latest/dev/virtualenvs/)，通过子目录下的 `.gitignore` 将虚拟环境文件设置为[不上传](http://blog.csdn.net/nyist327/article/details/39207383)。
- 完成 jieba_seg.py 和 wrt2vec.py

### 2016 年12月3日
- 参考 http://stevenloria.com/finding-important-words-in-a-document-using-tf-idf/ ，实现了能运行的 tf-idf。


## 4. 分布式协作开发

### 4.1 git 分布式协作

- 如往常一般 new 一个 repository。

- 点击 repository 中的 Settings，然后点击左侧的 Collaborators。

- 在文本框中输入小伙伴的 id，点击 Add collaborator，小伙伴同意后，就可以愉快地一起工作啦。

- **每次工作前，记得通过 `git pull` 来拉取最新项目。每次工作后，记得通过 `git push` 来上传项目更新。**


### 4.2 代码整合

我觉得相对独立地开发并没有错误，因为我们的代码本来就是相对独立的。而且我也提供了前后端的同一模板，每个独立的子模块都应该能够独立地跑起来。

代码整合的工作如下：

- 统一的环境配置（virtualenv+python3）

- 将每个独立子模块的 server.py 抽取出来，形成一个整合的 server.py；这个过程因为有统一的前后端模板，所以只有子模块没有问题，这里也不应该存在问题。

- 注意配置好模型文件和前端文件的路径。这个可以使用简单的拷贝文件命令就能实现。