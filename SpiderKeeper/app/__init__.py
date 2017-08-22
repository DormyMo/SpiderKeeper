# Import flask and template operators
import logging
import traceback

import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask import jsonify
from flask_basicauth import BasicAuth
from flask_restful import Api
from flask_restful_swagger import swagger
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

import SpiderKeeper
from SpiderKeeper import config

# Define the WSGI application object
app = Flask(__name__)
# Configurations
app.config.from_object(config)

# Logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
app.logger.setLevel(app.config.get('LOG_LEVEL', "INFO"))
app.logger.addHandler(handler)

# swagger
api = swagger.docs(Api(app), apiVersion=SpiderKeeper.__version__, api_spec_url="/api",
                   description='SpiderKeeper')
# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app, session_options=dict(autocommit=False, autoflush=True))


@app.teardown_request
def teardown_request(exception):
    if exception:
        db.session.rollback()
        db.session.remove()
    db.session.remove()

# Define apscheduler
scheduler = BackgroundScheduler()


class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())


# Sample HTTP error handling
# @app.errorhandler(404)
# def not_found(error):
#     abort(404)


@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    app.logger.error(traceback.print_exc())
    return jsonify({
        'code': code,
        'success': False,
        'msg': str(e),
        'data': None
    })


# Build the database:
from SpiderKeeper.app.spider.model import *


def init_database():
    db.init_app(app)
    db.create_all()


# regist spider service proxy
from SpiderKeeper.app.proxy.spiderctrl import SpiderAgent
from SpiderKeeper.app.proxy.contrib.scrapy import ScrapydProxy

agent = SpiderAgent()


def regist_server():
    if app.config.get('SERVER_TYPE') == 'scrapyd':
        for server in app.config.get("SERVERS"):
            agent.regist(ScrapydProxy(server))


from SpiderKeeper.app.spider.controller import api_spider_bp

# Register blueprint(s)
app.register_blueprint(api_spider_bp)

# start sync job status scheduler
from SpiderKeeper.app.schedulers.common import sync_job_execution_status_job, sync_spiders, \
    reload_runnable_spider_job_execution

scheduler.add_job(sync_job_execution_status_job, 'interval', seconds=5, id='sys_sync_status')
scheduler.add_job(sync_spiders, 'interval', seconds=10, id='sys_sync_spiders')
scheduler.add_job(reload_runnable_spider_job_execution, 'interval', seconds=30, id='sys_reload_job')


def start_scheduler():
    scheduler.start()


def init_basic_auth():
    if not app.config.get('NO_AUTH'):
        basic_auth = BasicAuth(app)


def initialize():
    init_database()
    regist_server()
    start_scheduler()
    init_basic_auth()
