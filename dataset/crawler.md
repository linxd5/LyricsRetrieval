## 网易云音乐歌词数据爬取

使用 scrapy 框架，从歌单 [http://music.163.com/discover/playlist)](http://music.163.com/discover/playlist) 中开始 dfs 爬取歌曲列表。入口见 ./wymusic/spiders/mainCrawler.py 文件。

接着从歌曲 id 中，调用网易云音乐的 API 接口，下载歌词信息。见 ./lyrics/fetch_lyrics.py 文件。
