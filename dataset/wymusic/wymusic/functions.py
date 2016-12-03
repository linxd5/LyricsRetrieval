#!/usr/bin/env python
# coding=utf-8
import logging

class LinkFilter(object):

    _url_set = set()

    @classmethod
    def duplicate(cls, link):
        if link.url not in cls._url_set:
            cls._url_set.add(link.url)
            logging.log(logging.DEBUG, 'the song {url} has been crawled'.format(url=link.url))
            return True
        else:
            return False
