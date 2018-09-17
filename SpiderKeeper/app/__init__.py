import datetime
import traceback
from flask import Flask, session, jsonify
from flask_basicauth import BasicAuth
from werkzeug.exceptions import HTTPException

import SpiderKeeper
from SpiderKeeper.app.blueprints.dashboard.views import dashboard_bp
from SpiderKeeper.app.blueprints.dashboard.api import api
from SpiderKeeper.app.blueprints.dashboard.model import Project, SpiderInstance
from SpiderKeeper.app.proxy import agent
from SpiderKeeper.app.proxy.contrib.scrapy import ScrapydProxy
from SpiderKeeper.app.extensions.sqlalchemy import db


def register_server(app):
    if app.config.get('SERVER_TYPE') == 'scrapyd':
        for server in app.config.get("SERVERS"):
            agent.regist(ScrapydProxy(server))


def init_basic_auth(app):
    if not app.config.get('NO_AUTH'):
        BasicAuth(app)


def init_database(app):
    db.init_app(app)
    with app.app_context():
        # Extensions like Flask-SQLAlchemy now know what the "current" app
        # is while within this block. Therefore, you can now run........
        db.create_all()


def register_extensions(app):
    init_database(app)
    init_basic_auth(app)
    api.init_app(app)


def register_blueprints(app):
    # Register blueprint(s)
    app.register_blueprint(dashboard_bp)


def create_flask_application(config):
    # Define the WSGI application object
    app = Flask(__name__)
    # Configurations
    app.config.from_object(config)
    app.jinja_env.globals['sk_version'] = SpiderKeeper.__version__
    register_extensions(app)
    register_blueprints(app)
    register_server(app)

    @app.context_processor
    def inject_common():
        return dict(now=datetime.datetime.now(),
                    servers=agent.servers)

    @app.context_processor
    def inject_project():
        project_context = {}
        project = None
        projects = Project.query.all()
        project_context['project_list'] = projects
        if projects:
            project = projects[0]

        project_id = session.get('project_id')
        if isinstance(project_id, int):
            project = Project.query.get(project_id) or project

        if project:
            session['project_id'] = project.id
            project_context['project'] = project
            project_context['spider_list'] = [
                spider_instance.to_dict() for spider_instance in
                SpiderInstance.query.filter_by(project_id=project.id).all()]
        else:
            project_context['project'] = {}
        return project_context

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
    return app
