# -*- coding: utf-8 -*-

from apscheduler.schedulers.twisted import TwistedScheduler
from SpiderKeeper.scheduler.jobs import add_jobs


def run_scheduler(flask_app):
    scheduler = TwistedScheduler()
    add_jobs(scheduler, flask_app)
    scheduler.start()
