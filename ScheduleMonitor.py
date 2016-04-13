# coding:utf8
__author__ = 'modm'
from flask import request, json
import requests
import threading
import sqlite3
import time, datetime
from urllib import urlencode

import logging

logger = logging.getLogger('scheduleMonitor')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

CONFIG = {}
with open('dist/config/config.json', 'r') as f:
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
        cu.execute(
            "SELECT id,daemons,project,spider,params,interval,date_update,start_time,times FROM  spider_keeper WHERE times>0")
        rows = cu.fetchall()
        cu.close()
        for row in rows:
            id, daemons, project, spider, params, interval, date_update, start_time, times = row
            nowTimestamp = int(time.time() * 1000)
            if (nowTimestamp - date_update > interval * 60 * 60 * 1000) and times > 0:
                if start_time > 0 and start_time > nowTimestamp:
                    continue
                data = json.loads(params)
                data.update({'daemons': daemons or ""})
                res = requests.get(CONFIG['server'] + "/spider/start/", params=urlencode(data))
                if res.status_code == 200:
                    logger.info('processing : id : %d time : %s' % (id, datetime.datetime.today()))
                    cu = cx.cursor()
                    cu.execute("UPDATE spider_keeper SET date_update =?,times=? WHERE id=?",
                               (nowTimestamp, times - 1, id))
                    cx.commit()
                    cu.close()
                else:
                    logger.error('processing : id : %d time : %s' % (id, datetime.datetime.today()))

                time.sleep(5)  # checking each 5s

                if __name__ == '__main__':
                    threading.Thread(target=scanTask).start()
