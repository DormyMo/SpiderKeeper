# -*- coding: utf-8 -*-
from scrapyd.config import Config
from SpiderKeeper.scrapyd.app import create_spiderkeeper_application

application = create_spiderkeeper_application(Config())
