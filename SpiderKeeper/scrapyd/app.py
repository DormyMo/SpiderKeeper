# -*- coding: utf-8 -*-

from scrapyd.app import application as create_scrapyd_application
from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
from twisted.web.server import Site
from SpiderKeeper.app import create_flask_application, config as default_config
from SpiderKeeper.scheduler import run_scheduler


def create_spiderkeeper_application(scrapyd_config, flask_config=default_config):
    flask_app = create_flask_application(flask_config)
    run_scheduler(flask_app)
    app = create_scrapyd_application(scrapyd_config)
    resource = WSGIResource(reactor, reactor.getThreadPool(), flask_app)
    site = Site(resource)
    reactor.listenTCP(5000, site)
    return app
