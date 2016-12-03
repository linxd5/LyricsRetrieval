# coding=utf-8

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from wymusic.functions import LinkFilter
from wymusic.items import WymusicItem

import datetime


count_song = 0
count_playlist = 0


class Crawler(CrawlSpider):
    name = 'musicCrawler'
    rules = [
        Rule(LinkExtractor(allow='/song\?id=\d+'), follow=False, callback='parseSong', process_links='filterLinks'),
        Rule(LinkExtractor(allow='/playlist\?id=\d+'), follow=True, callback='parsePlaylist', process_links='filterLinks')
    ]
    start_urls = ['http://music.163.com/discover/playlist']
    allowed_domains = ['music.163.com']

    def parseSong(self, response):
        global count_song
        count_song += + 1
        print '-------->', response.url

        song_title = response.xpath('//em[@class="f-ff2"]/text()').extract()[0]     # this is a string
        song_singers = response.xpath('//span/a[@class="s-fc7"]/text()').extract()  # this is a list

        item = WymusicItem()
        item['itemType'] = 'song'
        item['songId'] = response.url.split('=')[1]
        item['songDate'] = self.getCurrentTime()
        item['songTitle'] = song_title
        item['songSingers'] = ''.join(song_singers)

        yield item


    def parsePlaylist(self, response):
        global count_playlist, count_song
        count_playlist += 1

        print count_playlist,'/', count_song, response.url, self.getCurrentTime()

        playlistTitle = response.xpath('//h2[@class="f-ff2 f-brk"]/text()').extract()[0]
        playlistDesc = ''.join(response.xpath('//p[@id="album-desc-more"]/text()').extract())

        # return item
        item = WymusicItem()
        item['itemType'] = 'playlist'
        item['playlistId'] = response.url.split('=')[1]
        item['playlistDate'] = self.getCurrentTime()
        item['playlistTitle'] = playlistTitle
        item['playlistDesc'] = playlistDesc
        yield item

    def filterLinks(self, links):
        return filter(LinkFilter.duplicate, links)

    def closed(reason):
        print reason
        global count_song, count_playlist
        print count_song, 'articles', count_playlist, 'categories'

    def getCurrentTime(self):
        now = datetime.datetime.now()
        now_string = now.strftime('%y-%m-%d %H:%M:%S')
        return now_string
