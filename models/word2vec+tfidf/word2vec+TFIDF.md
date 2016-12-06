## 1. 模型训练过程

- 对网易云音乐的数据进行清洗，去除掉与歌词无关的东西。
- 对处理好后的数据进行 jieba 分词，保存分词后的歌词 (`jieba_seg.py`)。
- 使用分词后的歌词，统计 TF-IDF。(`tf-idf.py`)
- 对于每一首歌，得到每一个分词的词向量。组合该分词的 TF-IDF，得到整篇歌词的向量表示(`wrt2vec.py`)。


## 2. 模型预测过程

- 从前端的文本框中获取歌词
- 计算查询歌词的 TF-IDF，组合得到查询歌词的向量表示。
- 与库中的每一首歌做相似度对比，得到推荐歌词。
- 向前端返回推荐歌词。


## 3. 进度报告

### 2016年12月6日

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

