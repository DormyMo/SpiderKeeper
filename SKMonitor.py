#coding:utf8
__author__ = 'modm'
from flask import request,json
import requests
import threading
import sqlite3
import time,datetime

SCRAPY_URL = 'http://localhost:6800'  #your scrapyd service

DATABASE = 'SpiderKeeper.db'
def scanTask():
    cx = sqlite3.connect(DATABASE)
    while True:
        try:
            cu = cx.cursor()
        except:
            cx = sqlite3.connect(DATABASE)
        cu.execute("select id,project,spider,params,interval,date_update,start_time,times from  spider_keeper where times>0")
        rows = cu.fetchall()
        cu.close()
        for row in rows:
            id,project,spider,params,interval,date_update,start_time,times = row
            nowTimestamp = int(time.time()*1000)
            if (nowTimestamp-date_update>interval*60*60*1000) and times>0:
                if start_time>0 and start_time>nowTimestamp:
                    continue
                res = requests.post(SCRAPY_URL+"/schedule.json",params=json.loads(params))
                if res.status_code==200:
                    print 'processing : ',str(id),str(datetime.datetime.today())
                    print res.json()
                    cu=cx.cursor()
                    cu.execute("update spider_keeper set date_update =?,times=? where id=?",(nowTimestamp,times-1,id))
                    cx.commit()
                    cu.close()
        time.sleep(5) #checking each 5s
if __name__ == '__main__':
    threading.Thread(target=scanTask).start()