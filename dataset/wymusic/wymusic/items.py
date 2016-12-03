# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WymusicItem(scrapy.Item):
    # define the fields for your item here like:
    itemType = scrapy.Field()
    songId = scrapy.Field()
    songDate = scrapy.Field()
    songTitle = scrapy.Field()
    songSingers = scrapy.Field()
    playlistId = scrapy.Field()
    playlistDate = scrapy.Field()
    playlistTitle= scrapy.Field()
    playlistDesc = scrapy.Field()
