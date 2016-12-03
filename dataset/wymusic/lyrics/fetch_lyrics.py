# coding: utf-8

import gevent.monkey
import gevent
import requests
import random
import time
import pymongo

gevent.monkey.patch_socket()

mainurl = "http://music.163.com/api/song/lyric?os=pc&lv=-1&kv=-1&tv=-1&id="
user_agent = "User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"

USER_AGENT_LIST= [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
    "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
    "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
    "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
    "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
    "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
    "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
    "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
    "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
    "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
    "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]

def exeTime(func):
    def newFunc(*args, **args2):
        start = time.time()
        back = func(*args, **args2)
        print "%.3f taken for %s" % (time.time() - start, func.__name__)
        return back
    return newFunc

def getUrlsFromFile(filename):
    with open('c.csv', 'r') as f:
        i = 0
        batch_urls = []
        while(True):
            id = f.readline()
            i += 1
            if id:
                batch_urls.append(mainurl + id.strip())
                if i % 1 == 0:
                    yield batch_urls
                    batch_urls = []
            else:
                if len(batch_urls) > 0:
                    yield batch_urls
                return


def fetchData(batch_urls):
    headers = {"USER_AGENT":random.choice(USER_AGENT_LIST)}
    jobs = [gevent.spawn(requests.get, url, headers=headers, timeout=1) for url in batch_urls]
    gevent.joinall(jobs)
    batch_results = [job.value for job in jobs]
    return batch_results

def handleBatchData(total_count, db, batch_urls, batch_results):
    count_uncollected = 0
    count_nolyric = 0
    lyrics = ''
    for i, r in enumerate(batch_results):
        if r:
            r = r.json()
            if r.has_key('uncollected'):
                count_uncollected += 1
            elif r.has_key('nolyric'):
                count_nolyric += 1
            elif r.has_key('lrc'):
                if r['lrc'].has_key('lyric'):
                    lyrics = r['lrc']['lyric']
                else:
                    count_nolyric += 1
            else:
                print i, "exception!!"
            db['lyrics'].insert({'id':batch_urls[i].split('=')[-1], 'lyrics':lyrics})
    print 'total: %d, count_uncollected: %d, count_nolyric: %d, len of lyrics: %d' %(total_count, count_uncollected, count_nolyric, len(lyrics))

@exeTime
def mainPipline():
    client = pymongo.MongoClient()
    db = client["wymusic"]
    total_count = 0
    for batch_urls in getUrlsFromFile(''):
        total_count += len(batch_urls)
        batch_results = fetchData(batch_urls)
        handleBatchData(total_count, db, batch_urls, batch_results)
        #time.sleep(0.001)
    client.close()

if __name__ == '__main__':
    mainPipline()
