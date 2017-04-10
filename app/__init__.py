# Import flask and template operators
import logging
import traceback

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask import jsonify
from flask.ext.restful import Api
from flask.ext.restful_swagger import swagger
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

# Define the WSGI application object
app = Flask(__name__)
# Configurations
app.config.from_object('config')

# Logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(app.config.get('BASE_DIR') + '/app/logs/%s' % 'sk.log', 'w', 'utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
app.logger.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

# swagger
api = swagger.docs(Api(app), apiVersion='2.0.0', api_spec_url="/api",
                   description='SpiderKeeper v2.0')
# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

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
from app.spider.model import *

db.create_all()

# regist spider service proxy
from app.proxy.spiderctrl import SpiderAgent
from app.proxy.contrib.scrapy import ScrapydProxy

agent = SpiderAgent()
for host, port in app.config.get("SCRAPYD_SERVICES"):
    agent.regist(ScrapydProxy(host=host, port=port))

from app.spider.controller import api_spider_bp

# Register blueprint(s)
app.register_blueprint(api_spider_bp)

# start sync job status scheduler
from app.schedulers.common import sync_job_execution_status_job, reload_runnable_spider_job_execution

scheduler.add_job(sync_job_execution_status_job, 'interval', seconds=3, id='sys_sync_status')
scheduler.add_job(reload_runnable_spider_job_execution, 'interval', seconds=5, id='sys_reload_job')
scheduler.start()
