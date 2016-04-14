#coding:utf8
__author__ = 'modm'
import flask
import json as defaultJson
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
    CONFIG = defaultJson.load(f)
f.close
scrapydMapping = {}
for scrapyd in CONFIG['scrapyd']:
    scrapydMapping[scrapyd['name']] = scrapyd['server']

DATABASE = 'SpiderKeeper.db'
#init
cx = sqlite3.connect(DATABASE)
cu=cx.cursor()
cu.execute("CREATE TABLE IF NOT EXISTS spider_keeper (id integer PRIMARY KEY AUTOINCREMENT,daemons varchar(200),project varchar(50),spider varchar(50),params varchar(200) NULL,interval integer,start_time integer,times integer,date_update integer)")
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

def _request(url):
    retryTime = 5
    res = None
    for i in range(retryTime):
        try:
            res = requests.get(url)#self.proxyUtil.getRandomProxy())
            if res.status_code !=200:
                continue
            break
        except:
            continue
    return res

def _request_post(url):
    retryTime = 5
    res = None
    for i in range(retryTime):
        try:
            res = requests.post(url)#self.proxyUtil.getRandomProxy())
            if res.status_code !=200:
                continue
            break
        except:
            continue
    return res
#### schedule servlet
@app.route('/config/config.json')
@allow_cross_domain
def config():
    return json.dumps(CONFIG)

@app.route('/schedule/add/')
@allow_cross_domain
def schedule_add():
    project = request.args.get('project')
    spider = request.args.get('spider')
    paramStr = request.args.get('params')
    startTime = request.args.get('startTime')
    interval = request.args.get('interval')
    times = request.args.get('times')
    daemons = request.args.get('daemons')
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
        cu.execute("INSERT INTO spider_keeper(daemons,project,spider,params,start_time,interval,times,date_update) values(?,?,?,?,?,?,?,?)",(daemons,project,spider,json.dumps(params),startTimestamp,interval,times,int(time.time()*1000)))
        cx.commit()
        return json.dumps({'status':'ok'})
    else:
        return json.dumps({'status':'error'})
@app.route('/schedule/list/')
@allow_cross_domain
def scheduler_list():
    project = request.args.get('project')
    cu = get_db().cursor()
    cu.execute("select project,spider,params,interval,date_update,start_time,times,id,daemons from  spider_keeper where times>0 and project = ?",(project,))
    rows = cu.fetchall()
    result =[]
    for row in rows:
        result.append({'daemons':row[8],'project':row[0],'spider':row[1],'params':row[2],'interval':row[3],'date_update':row[4],'start_time':row[5],'times':row[6],'id':row[7]})
    return json.dumps({'status':'ok','data':result})

@app.route('/schedule/del/')
@allow_cross_domain
def schedule_del():
    id = request.args.get('id')
    if id:
        cu = get_db().cursor()
        cu.execute("delete from spider_keeper where id = ?",(id,))
        print get_db().commit()
        return json.dumps({'status':'ok'})
    else:
        return json.dumps({'status':'error'})

@app.route('/project/list/')
@allow_cross_domain
def project_list():
    server = CONFIG['scrapyd'][0]['server']
    res =  _request("%s/listprojects.json?%s"    %(server,request.query_string))
    if res:
        return json.dumps(res.json())
    else: 
        return json.dumps({'status':'error'})


@app.route('/spider/list/')
@allow_cross_domain
def spider_list():
    server = CONFIG['scrapyd'][0]['server']
    res =  _request("%s/listspiders.json?%s"    %(server,request.query_string))
    if res:
        return json.dumps(res.json())
    else: 
        return json.dumps({'status':'error'})

def getAllDaemonStatus():
    result = []
    for scrapyd in CONFIG['scrapyd']:
        res = _request("%s/daemonstatus.json"    %(scrapyd['server']))
        if res:
            data = res.json()
            data.update({'name':scrapyd['name']})
            data.update({'server':scrapyd['server']})
            result.append(data)
    return result

def getFreeDaemon():
    daemons = getAllDaemonStatus()
    select_daemon = daemons[0]
    for daemon in daemons:
        if daemon['running'] < select_daemon['running']:
            select_daemon = daemon
    return daemon



@app.route('/spider/start/')
@allow_cross_domain
def spider_start():
    daemons = [{'name':daemonName,'server':scrapydMapping[daemonName]} for daemonName in (request.args.get('daemons').split(u',') if request.args.get('daemons') else [])]
    if not daemons:
        daemons = [getFreeDaemon()]
    result = []
    for daemon in daemons:
        res =  _request_post("%s/schedule.json?%s"    %(daemon['server'],request.query_string))
        if res:
            data = res.json()
            data.update({'daemon':daemon['name']})
            result.append(data)
        else: 
            data = {'status':'error'}
            data.update({'daemon':daemon['name']})
            result.append(data)
    return json.dumps({'status':'ok','data':result})

@app.route('/spider/cancel/')
@allow_cross_domain
def spider_cancel():
    daemons = [{'name':daemonName,'server':scrapydMapping[daemonName]} for daemonName in (request.args.get('daemons').split(u',') if request.args.get('daemons') else [])]
    for daemon in daemons:
        res =  _request_post("%s/cancel.json?%s"    %(daemon['server'],request.query_string))
    if res:
        return json.dumps(res.json())
    else: 
        return json.dumps({'status':'error'})

@app.route('/log/')
@allow_cross_domain
def log():
    daemon = request.args['daemon']
    project = request.args['project']
    spider = request.args['spider']
    jobId = request.args['jobId']
    res =  _request("%s/logs/%s/%s/%s.log"    %(scrapydMapping[daemon],project,spider,jobId))
    html = '<html><body style="background-color:#F3F2EE;"><p style="font-size: 12px;line-height: 1.5em;color: #1f0909;text-align: left">'
    html += res.content.replace('\n', '<br>') + '</p></body></html>'
    return html

@app.route('/job/list/<status>/')
@allow_cross_domain
def job_list(status):
    daemons = [{'name':daemonName,'server':scrapydMapping[daemonName]} for daemonName in (request.args.get('daemons').split(u',') if request.args.get('daemons') else [])]
    if not daemons:
        return json.dumps({'status':'error','data':[]})
    result = {}
    for daemon in daemons:
        res = _request("%s/listjobs.json?%s"    %(daemon['server'],request.query_string))
        if res:
            data = []
            if status == 'all':
                result[daemon['name']] = res.json()
            else:
                data = res.json().get(status,[])
                for item in data:
                    start_time = end_time = running_time = None
                    if 'start_time' in item.keys():
                        start_time = datetime.datetime.strptime(item['start_time'],"%Y-%m-%d %H:%M:%S.%f")
                        item['start_time'] = start_time.strftime("%Y-%m-%d %H:%M:%S")
                    if 'end_time' in item.keys():
                        end_time = datetime.datetime.strptime(item['end_time'],"%Y-%m-%d %H:%M:%S.%f")
                        item['end_time'] = end_time.strftime("%Y-%m-%d %H:%M:%S")
                    if start_time and end_time:
                        running_time = "%.2f"    %((end_time - start_time).total_seconds()/3600)
                        item['running_time'] = running_time
                result[daemon['name']] = {status:data}
    return json.dumps({'status':'ok','data':result})


@app.route('/daemon/status/')
@allow_cross_domain
def daemon_status():
    daemons = request.args.get('daemons').split(',') if request.args.get('daemons') else []
    if not daemons:
        return json.dumps({'status':'error','data':[]})
    result = []
    for daemonName in daemons:
        res = _request("%s/daemonstatus.json"    %(scrapydMapping[daemonName]))
        if res:
            data = res.json()
            data.update({'name':daemonName})
            result.append(data)
        else:
            result.append({'status':'error','name':daemonName})

    return json.dumps({'status':'ok','data':result})

#### static file provider
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
    app.run(host='0.0.0.0',port=8080,debug=False)