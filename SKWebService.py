#coding:utf8
__author__ = 'modm'
import flask
from flask import Flask
from flask import request,json
from functools import wraps
from flask import make_response
import requests
import threading
import sqlite3
from flask import g
import os
import time,datetime

SCRAPY_URL = 'http://localhost:6800' #your scrapyd service

DATABASE = 'SpiderKeeper.db'
#init
cx = sqlite3.connect(DATABASE)
cu=cx.cursor()
cu.execute("CREATE TABLE IF NOT EXISTS spider_keeper (id integer PRIMARY KEY AUTOINCREMENT,project varchar(50),spider varchar(50),params varchar(200) NULL,interval integer,start_time integer,times integer,date_update integer)")
cx.commit()


def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = '*'
        rst.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers ="Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst
    return wrapper_fun

app = Flask(__name__)
def connect_to_database():
    return sqlite3.connect(DATABASE)
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
def connect_db():
    return sqlite3.connect("SpiderKeeper.db")
#### schedule servlet
@app.route('/schedule')
@allow_cross_domain
def schedule():
    project = request.args.get('project')
    spider = request.args.get('spider')
    paramStr = request.args.get('params')
    startTime = request.args.get('startTime')
    interval = request.args.get('interval')
    times = request.args.get('times')
    startTimestamp = 0
    if startTime:
        startTimestamp = time.mktime(datetime.datetime.strptime(startTime,'%Y-%m-%d %H:%M:%S').timetuple())*1000
    if project and spider and interval:
        params ={
            "project":project,
            "spider":spider};
        if paramStr:
            paramArray = paramStr.split(u',')
            for i in range(len(paramArray)):
                kv = paramArray[i].split(u'=')
                params[kv[0]] = kv[1]
        cx= get_db()
        cu = get_db().cursor()
        cu.execute("INSERT INTO spider_keeper(project,spider,params,start_time,interval,times,date_update) values(?,?,?,?,?,?,?)",(project,spider,json.dumps(params),startTimestamp,interval,times,int(time.time()*1000)))
        cx.commit()
        return json.dumps({'status':'ok'})
    else:
        return json.dumps({'status':'error'})
@app.route('/getScheduler')
@allow_cross_domain
def getScheduler():
    project = request.args.get('project')
    cu = get_db().cursor()
    cu.execute("select project,spider,params,interval,date_update,start_time,times,id from  spider_keeper where times>0 and project = ?",(project,))
    rows = cu.fetchall()
    result =[]
    for row in rows:
        result.append({'project':row[0],'spider':row[1],'params':row[2],'interval':row[3],'date_update':row[4],'start_time':row[5],'times':row[6],'id':row[7]})
    return json.dumps({'status':'ok','data':result})
@app.route('/removeSchedule')
@allow_cross_domain
def removeSchedule():
    id = request.args.get('id')
    if id:
        cu = get_db().cursor()
        cu.execute("delete from spider_keeper where id = ?",(id,))
        print get_db().commit()
        return json.dumps({'status':'ok'})
    else:
        return json.dumps({'status':'error'})

#### static servlet
@app.route('/')
def root():
    print request.path
    return static_file('dist/index.html')
file_suffix_to_mimetype = {
    '.css': 'text/css',
    '.jpg': 'image/jpeg',
    '.html': 'text/html',
    '.ico': 'image/x-icon',
    '.png': 'image/png',
    '.js': 'application/javascript',
    '.ttf': 'application/font-ttf',
    '.woff2':'application/font-woff2'
}

import subprocess
modulesSubPath = '/status/server/modules/shell_files/'
serverPath = os.path.dirname(os.path.realpath(__file__))
def static_file(path):
    try:
        #print path
        if path.startswith("styles"):
            path="dist/"+path
        if path.startswith("scripts"):
            path="dist/"+path
        if path.startswith("fonts"):
            path="dist/"+path
        if path.startswith("status/server"):
            data = ''
            contentType = 'text/html'
            module = request.args.get('module')
            output = subprocess.Popen(
            serverPath + modulesSubPath + module + '.sh',
            shell = True,
            stdout = subprocess.PIPE)
            data = output.communicate()[0]
            return data
        f = open(path)
    except IOError, e:
        flask.abort(404)
        return
    root, ext = os.path.splitext(path)
    if ext in file_suffix_to_mimetype:
        return flask.Response(f.read(), mimetype=file_suffix_to_mimetype[ext])
    return f.read()

if __name__ == '__main__':
    app.add_url_rule('/<path:path>', 'static_file', static_file)
    app.run(host='0.0.0.0',port=8080,debug=True)