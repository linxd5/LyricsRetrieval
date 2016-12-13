# coding: utf-8

import gevent.monkey
import gevent
import requests
import random
import time
import pymongo
import json

gevent.monkey.patch_socket()

mainurl = "http://music.163.com/api/song/detail/?ids=%%5B%d%%5D&id=%d"
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
        print("%.3f taken for %s" % (time.time() - start, func.__name__))
        return back
    return newFunc

def getUrlsFromFile(filename, batch_size = 10):
    with open('big.csv', 'r') as f:
        i = 0
        batch_urls = []
        while(True):
            songid = f.readline()
            i += 1
            if songid:
                batch_urls.append(mainurl %(int(songid), int(songid)))
                if i % batch_size == 0:
                    yield batch_urls
                    batch_urls = []
            else:
                # consider the rest, which can not form a batch data
                if len(batch_urls) > 0:
                    yield batch_urls
                return


def fetchData(batch_urls):
    headers = {"USER_AGENT":random.choice(USER_AGENT_LIST)}
    jobs = [gevent.spawn(requests.get, url, headers=headers, timeout=2) for url in batch_urls]
    gevent.joinall(jobs)
    batch_results = [job.value for job in jobs]
    return batch_results

def handleBatchData(total_count, db, batch_urls, batch_results, fwrite):
    print('total count = %d' %(total_count))
    for i, r in enumerate(batch_results):
        songid = batch_urls[i].split('=')[-1]
        if r:
            data = {'songid':songid, 'data':json.loads(r.text)}
            db['song_detail'].insert(data)
        else:
            fwrite.write(songid + '\n')


@exeTime
def mainPipline():
    client = pymongo.MongoClient()
    db = client["wymusic"]
    total_count = 0
    fwrite = open('failed.txt', 'w')
    for batch_urls in getUrlsFromFile(''):
        total_count += len(batch_urls)
        batch_results = fetchData(batch_urls)
        handleBatchData(total_count, db, batch_urls, batch_results, fwrite)
        time.sleep(0.001)
    fwrite.close()
    client.close()

if __name__ == '__main__':
    try:
        mainPipline()
    except Exception:
        pass
