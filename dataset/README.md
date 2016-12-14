## 网易云音乐歌词数据爬取

### 步骤一
使用 scrapy 框架，从歌单 [http://music.163.com/discover/playlist](http://music.163.com/discover/playlist) 中开始 dfs 爬取歌曲列表。入口见 `./wymusic/spiders/mainCrawler.py` 文件。

爬取的数据存储在 MongoDB 数据库的 `wymusic.playlists` 和 `wymusic.songs` 中

### 步骤二
接着从歌曲 id 中，调用网易云音乐的 API 接口，下载歌词信息。见 `./lyrics/fetch_lyrics.py` 文件。

数据存储在 MongoDB 数据库的 `wymusic.lyrics` 中

### 步骤三
接着从歌曲 id 中，调用网易云音乐的 API 接口，下载详细信息。见 `./lyrics/fetch_song_details.py` 文件。

数据存储在 MongoDB 数据库的 `wymusic.song_detail` 中
