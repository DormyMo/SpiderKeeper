#coding:utf8
__author__ = 'modm'
from flask import request,json
import requests
import threading
import sqlite3
import time,datetime
from urllib import urlencode

import logging
logger = logging.getLogger('daemonService')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

CONFIG = {}
with open('dist/config/config.json','r') as f:
    CONFIG = json.load(f)
f.close
scrapydMapping = {}
for scrapyd in CONFIG['scrapyd']:
    scrapydMapping[scrapyd['name']] = scrapyd['server']

DATABASE = 'SpiderKeeper.db'
def scanTask():
    cx = sqlite3.connect(DATABASE)
    while True:
        try:
            cu = cx.cursor()
        except:
            cx = sqlite3.connect(DATABASE)
        cu.execute("select id,daemons,project,spider,params,interval,date_update,start_time,times from  spider_keeper where times>0")
        rows = cu.fetchall()
        cu.close()
        for row in rows:
            id,project,daemons,spider,params,interval,date_update,start_time,times = row
            nowTimestamp = int(time.time()*1000)
            if (nowTimestamp-date_update>interval*60*60*1000) and times>0:
                if start_time>0 and start_time>nowTimestamp:
                    continue
                data = json.loads(params)
                data.update({'daemons':daemons})
                res = requests.post(SCRAPY_URL+"/spider/start/",params=urlencode(data))
                if res.status_code==200:
                    logger.info('processing : '+str(id)+str(datetime.datetime.today()))
                    cu=cx.cursor()
                    cu.execute("update spider_keeper set date_update =?,times=? where id=?",(nowTimestamp,times-1,id))
                    cx.commit()
                    cu.close()
        time.sleep(5) #checking each 5s
if __name__ == '__main__':
    threading.Thread(target=scanTask).start()
